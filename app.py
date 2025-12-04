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
        "HTML/CSS 마크업 이해",
        "JavaScript 기본 문법 및 DOM 조작",
        "프론트엔드 프레임워크 경험 (예: React, Vue)",
        "웹 프레임워크 사용 경험 (예: Django, Spring, Node.js)",
        "REST API 연동 경험",
        "반응형 웹, 크로스 브라우저 이슈 이해",
        "Git 등 형상관리 도구 사용 경험",
    ],
    "서버개발": [
        "하나 이상의 서버 언어 사용 경험 (예: Java, Python, Node.js)",
        "웹 프레임워크 경험 (예: Spring Boot, Django, Express)",
        "RDBMS 설계 및 SQL 활용",
        "API 설계 및 문서화 경험",
        "배포/운영 환경 이해 (Linux, Cloud, Docker 등)",
        "로그 분석 및 모니터링 기본",
    ],
    "데이터분석": [
        "Python 기반 데이터 분석 (Pandas, NumPy)",
        "시각화 도구 활용 (Matplotlib, Seaborn, Plotly 등)",
        "기본 통계 지식 및 가설검정",
        "기계학습 라이브러리 사용 (scikit-learn 등)",
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
    """
    category 컬럼에서 선택 가능한 직무 목록 가져오기.
    """
    return sorted(df["category"].dropna().unique().tolist())


def filter_by_category(df: pd.DataFrame, category_value: str):
    """
    선택한 category(직무) 기준으로 데이터 필터링.
    - count 내림차순 정렬
    - 인덱스 1부터 시작
    - word -> '요구 역량'으로 컬럼명 변경
    """
    filtered = df[df["category"] == category_value].copy()
    filtered = filtered.sort_values("count", ascending=False).reset_index(drop=True)

    # 인덱스 1부터 시작
    filtered.index = range(1, len(filtered) + 1)

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

    # === 2️⃣ 선택한 분야 상위 키워드 ===
    filtered_df = filter_by_category(df, selected_category)

    st.subheader("2️⃣ 선택한 분야 상위 키워드")

    if filtered_df.empty:
        st.warning("해당 데이터가 없습니다.")
    else:
        # 🔹 전체 공고 수(total_posts) 캡션으로 표시
        total_posts_value = None
        if "total_posts" in filtered_df.columns:
            try:
                total_posts_value = int(filtered_df["total_posts"].iloc[0])
            except Exception:
                total_posts_value = filtered_df["total_posts"].iloc[0]

        if total_posts_value is not None:
            st.caption(f"전체 공고 수: {total_posts_value}")

        # 🔹 표에서는 '요구 역량'과 'count'만 보여주기
        drop_cols = [c for c in ["total_posts", "ratio"] if c in filtered_df.columns]
        display_df = filtered_df.drop(columns=drop_cols, errors="ignore")

        view_cols = ["요구 역량", "count"]
        existing_cols = [c for c in view_cols if c in display_df.columns]

        if not existing_cols:
            st.error(
                f"표시할 컬럼(요구 역량, count)을 찾을 수 없습니다. "
                f"현재 컬럼: {list(display_df.columns)}"
            )
            st.stop()

        display_df = display_df[existing_cols]

        st.dataframe(display_df, use_container_width=True)

        

        # === 3️⃣ 세부 역량 보기 ===
        st.subheader("3️⃣ 선택한 요구 역량의 세부 역량")

        skill_options = display_df["요구 역량"].unique().tolist()

        selected_skill = st.selectbox(
            "세부 역량을 보고 싶은 요구 역량을 선택하세요:",
            options=skill_options,
        )

        st.write(f"**선택한 요구 역량:** {selected_skill}")

        details = DETAIL_MAP.get(selected_skill)

        if details:
            st.markdown("**🔍 이 역량을 위해 도움이 되는 세부 역량 예시:**")
            for d in details:
                st.markdown(f"- {d}")
        else:
            st.caption("아직 이 역량에 대한 세부 역량 정보는 준비 중입니다.")

    


if __name__ == "__main__":
    main()
