import os
import pandas as pd
import streamlit as st

# === 0. 경로/파일 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_NAME = "직무별_단순빈도_TOP10(final).csv"
CSV_PATH = os.path.join(BASE_DIR, CSV_NAME)

# === 0-1. 세부 역량 매핑 (여기에 많이 넣어도 됨) ===
DETAIL_MAP = {
    "웹개발": [
        "HTML/CSS 마크업 기본 및 시맨틱 태그 이해",
        "JavaScript 기본 문법 및 DOM 조작",
        "프론트엔드 프레임워크 사용 경험 (예: React, Vue)",
        "백엔드 API 연동 및 JSON 처리 경험",
        "웹 프레임워크 경험 (예: Django, Spring, Node.js 등)",
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
    # TODO: 계속 추가 가능
}


# === 1. 데이터 로드 함수 ===
@st.cache_data
def load_keyword_data():
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
    return sorted(df["category"].dropna().unique().tolist())


def filter_by_category(df: pd.DataFrame, category_value: str):
    filtered = df[df["category"] == category_value].copy()
    filtered = filtered.sort_values("count", ascending=False).reset_index(drop=True)
    filtered.rename(columns={"word": "요구 역량"}, inplace=True)
    return filtered


def main():
    st.set_page_config(
        page_title="AI 역량 키워드 뷰어",
        layout="wide",
    )

    # === 화면 패딩 줄이기 ===
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📊 분야별 자주 요구되는 AI 역량 키워드")

    # 데이터 로드
    try:
        df = load_keyword_data()
    except Exception as e:
        st.error(f"❌ 데이터 오류 발생: {e}")
        st.stop()

    st.caption("현재 CSV 컬럼: " + ", ".join(df.columns.astype(str)))

    # 1️⃣ 직무 선택
    st.subheader("1️⃣ 관심 있는 직무 선택")

    categories = get_categories(df)
    if not categories:
        st.error("category 컬럼에 값이 없습니다. CSV 데이터를 확인해 주세요.")
        st.stop()

    selected_category = st.selectbox(
        "관심 있는 분야를 선택하세요:",
        options=categories,
        index=0,
    )

    st.write(f"### 선택한 분야: **{selected_category}**")

    # 2️⃣ 상위 키워드 표 + 라디오 선택
    st.subheader("2️⃣ 선택한 분야 상위 키워드")

    filtered_df = filter_by_category(df, selected_category)
    if filtered_df.empty:
        st.warning("해당 데이터가 없습니다.")
        st.stop()

    # 전체 공고 수 표시
    if "total_posts" in filtered_df.columns:
        total_posts_value = filtered_df["total_posts"].iloc[0]
        st.caption(f"전체 공고 수: {total_posts_value}")

    table_df = filtered_df[["요구 역량", "count"]].copy()
    table_df.index = range(1, len(table_df) + 1)

    st.dataframe(table_df, use_container_width=True)

    st.markdown("**세부 역량을 보고 싶은 키워드를 선택하세요.**")

    skill_options = table_df["요구 역량"].tolist()
    selected_skill = st.radio(
        "요구 역량 선택:",
        options=skill_options,
        index=0,
        horizontal=False,
    )

    # 🔍 세부 역량 표시
    st.markdown("---")
    st.markdown(f"### 🔍 {selected_skill}의 세부 역량")

    details = DETAIL_MAP.get(selected_skill)
    if details:
        for d in details:
            st.markdown(f"- {d}")
    else:
        st.caption("아직 이 역량에 대한 세부 역량 정보는 준비 중입니다.")


if __name__ == "__main__":
    main()
