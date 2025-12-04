import os
import pandas as pd
import streamlit as st

# === 0. 경로/파일 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_NAME = "직무별_단순빈도_TOP10(final).csv"
CSV_PATH = os.path.join(BASE_DIR, CSV_NAME)

# === 0-1. 세부 역량 매핑 (예시) ===
DETAIL_MAP = {
    "웹개발": [
        "HTML/CSS 마크업 기본 및 시맨틱 태그 이해",
        "JavaScript 기본 문법 및 DOM 조작",
        "프론트엔드 프레임워크 사용 경험 (예: React, Vue)",
        "웹 프레임워크 사용 경험 (예: Django, Spring, Node.js 등)",
        "REST API 연동 및 JSON 데이터 처리 경험",
        "반응형 웹, 크로스 브라우저 이슈 이해",
        "Git 등 형상관리 도구 사용 경험",
    ],
    "서버개발": [
        "하나 이상의 서버 언어 사용 경험 (예: Java, Python, Node.js)",
        "웹 프레임워크 경험 (예: Spring Boot, Django, Express 등)",
        "RDBMS 설계 및 SQL 활용 능력",
        "API 설계 및 문서화 경험",
        "배포/운영 환경 이해 (Linux, Cloud, Docker 등)",
        "로그 분석 및 모니터링 기본",
    ],
    "데이터분석": [
        "Python 기반 데이터 분석 (Pandas, NumPy 등)",
        "시각화 도구 활용 (Matplotlib, Seaborn, Plotly 등)",
        "기본 통계 지식 및 가설검정 이해",
        "기계학습 라이브러리 사용 경험 (scikit-learn 등)",
        "데이터 전처리 및 피처 엔지니어링",
        "SQL을 활용한 데이터 추출 경험",
    ],
    # 필요하면 계속 추가!
}


# === 1. 데이터 로드 함수 ===
@st.cache_data
def load_keyword_data():
    """
    직무별_단순빈도_TOP10(final).csv 파일을 읽어서 DataFrame으로 반환.
    인코딩 문제 대비: utf-8-sig → cp949 순으로 시도.
    필수 컬럼: category, word, count, total_posts
    """
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="cp949")

    required_cols = {"category", "word", "count", "total_posts"}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"다음 컬럼이 CSV에 없습니다: {missing}")

    return df


def get_categories(df: pd.DataFrame):
    """category 컬럼에서 선택 가능한 직무 목록 가져오기."""
    return sorted(df["category"].dropna().unique().tolist())


def filter_by_category(df: pd.DataFrame, category_value: str):
    """
    선택한 category(직무) 기준으로 데이터 필터링.
    - count 내림차순 정렬
    - '순위' 컬럼(1부터 시작) 추가
    - word -> '요구 역량'으로 컬럼명 변경
    """
    filtered = df[df["category"] == category_value].copy()
    filtered = filtered.sort_values("count", ascending=False).reset_index(drop=True)

    # 순위 컬럼 (1부터 시작)
    filtered["순위"] = range(1, len(filtered) + 1)

    # word → 요구 역량
    filtered.rename(columns={"word": "요구 역량"}, inplace=True)

    return filtered


# === 2. Streamlit 메인 앱 ===
def main():
    st.set_page_config(
        page_title="AI 역량 키워드 뷰어",
        layout="wide",
    )

    st.title("📊 분야별 자주 요구되는 AI 역량 키워드")

    # 데이터 로드
    try:
        df = load_keyword_data()
    except Exception as e:
        st.error(f"❌ 데이터 오류 발생: {e}")
        st.stop()

    st.caption("현재 CSV 컬럼: " + ", ".join(df.columns.astype(str)))

    # === 1️⃣ 관심 있는 직무 선택 (selectbox) ===
    st.subheader("1️⃣ 관심 있는 직무 선택")

    categories = get_categories(df)
    if not categories:
        st.error("category 컬럼에 값이 없습니다. CSV 데이터를 확인해 주세요.")
        st.stop()

    selected_category = st.selectbox(
        "관심 있는 직무(분야)를 선택하세요:",
        options=categories,
        index=0,
    )

    st.write(f"### 선택한 분야: **{selected_category}**")

    # === 2️⃣ 선택한 분야 상위 키워드 (행의 '선택' → 세부 역량) ===
    st.subheader("2️⃣ 선택한 분야 상위 키워드 (행의 '선택'을 클릭하면 세부 역량이 나와요)")

    filtered_df = filter_by_category(df, selected_category)

    if filtered_df.empty:
        st.warning("해당 데이터가 없습니다.")
    else:
        # 전체 공고 수 표시
        total_posts_value = None
        if "total_posts" in filtered_df.columns:
            try:
                total_posts_value = int(filtered_df["total_posts"].iloc[0])
            except Exception:
                total_posts_value = filtered_df["total_posts"].iloc[0]

        if total_posts_value is not None:
            st.caption(f"전체 공고 수: {total_posts_value}")

        # 테이블용 기본 데이터 (순위, 요구 역량, count)
        drop_cols = [c for c in ["total_posts", "ratio"] if c in filtered_df.columns]
        base_df = filtered_df.drop(columns=drop_cols, errors="ignore")

        view_cols = ["순위", "요구 역량", "count"]
        existing_cols = [c for c in view_cols if c in base_df.columns]
        if not existing_cols:
            st.error(
                f"표시할 컬럼(순위, 요구 역량, count)을 찾을 수 없습니다. "
                f"현재 컬럼: {list(base_df.columns)}"
            )
            st.stop()

        base_df = base_df[existing_cols]

        # ✅ 카테고리가 바뀌면 상태 초기화
        state_key = "skills_table_state"
        selected_idx_key = "selected_row_idx"

        if (
            state_key not in st.session_state
            or st.session_state.get("current_category") != selected_category
        ):
            table_df = base_df.copy()
            table_df["선택"] = False
            st.session_state[state_key] = table_df
            st.session_state["current_category"] = selected_category
            st.session_state[selected_idx_key] = None
        else:
            # 기존 상태 유지
            prev_df = st.session_state[state_key]
            table_df = base_df.copy()
            if "선택" not in prev_df.columns:
                prev_df["선택"] = False
            table_df["선택"] = prev_df["선택"].reindex(table_df.index).fillna(False)

        st.caption("※ 보고 싶은 '요구 역량' 행의 **선택** 칸을 클릭하면, 아래에 세부 역량이 나타납니다. (항상 하나만 선택됩니다)")

        # 🔹 편집 가능한 테이블 (체크박스 포함)
        editor_df = st.data_editor(
            table_df,
            key="skills_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "선택": st.column_config.CheckboxColumn(
                    "선택",
                    help="세부 역량을 보고 싶은 항목을 체크하세요. (하나만 선택됩니다)",
                ),
                "순위": st.column_config.NumberColumn("순위", disabled=True),
                "요구 역량": st.column_config.TextColumn("요구 역량", disabled=True),
                "count": st.column_config.NumberColumn("count", disabled=True),
            },
        )

        # === ✅ 여기서 "무조건 하나만" 선택되도록 강제 ===
        df_final = editor_df.copy()

        selected_indices = df_final.index[df_final.get("선택", False) == True].tolist()

        if not selected_indices:
            selected_idx = None
        else:
            # 여러 개 체크되어 있으면 "가장 마지막에 체크된 것"만 남기고 나머지는 해제
            selected_idx = selected_indices[-1]
            df_final["선택"] = False
            if selected_idx in df_final.index:
                df_final.loc[selected_idx, "선택"] = True

        # 상태 저장
        st.session_state[state_key] = df_final
        st.session_state[selected_idx_key] = selected_idx

        # === 아래에 세부 역량 출력 ===
        st.markdown("---")
        st.markdown("### 🔍 선택한 요구 역량의 세부 역량")

        if selected_idx is None:
            st.caption("위 표에서 보고 싶은 요구 역량 행의 **선택** 칸을 클릭하면, 이 아래에 세부 역량이 나타납니다.")
        else:
            try:
                selected_skill = df_final.loc[selected_idx, "요구 역량"]
            except Exception:
                selected_skill = None

            if not selected_skill:
                st.caption("선택한 요구 역량 정보를 불러오는 중 문제가 발생했습니다.")
            else:
                st.write(f"**선택한 요구 역량:** {selected_skill}")

                details = DETAIL_MAP.get(selected_skill)

                if details:
                    st.markdown("**이 역량을 위해 도움이 되는 세부 역량 예시:**")
                    for d in details:
                        st.markdown(f"- {d}")
                else:
                    st.caption("아직 이 역량에 대한 세부 역량 정보는 준비 중입니다.")

    


if __name__ == "__main__":
    main()
