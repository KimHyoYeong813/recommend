import os
import pandas as pd
import streamlit as st

# === 0. 경로/파일 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_NAME = "직무별_단순빈도_TOP10(final).csv"
CSV_PATH = os.path.join(BASE_DIR, CSV_NAME)


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

    # 필요한 컬럼이 있는지 확인
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
    count 기준 내림차순 정렬하고, ratio 컬럼(count/total_posts) 추가.
    """
    filtered = df[df["category"] == category_value].copy()
    filtered = filtered.sort_values("count", ascending=False).reset_index(drop=True)

    if "total_posts" in filtered.columns:
        filtered["ratio"] = filtered["count"] / filtered["total_posts"]

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
    except FileNotFoundError as e:
        st.error(f"❌ 데이터 파일을 찾을 수 없습니다.\n\n{e}")
        st.stop()
    except KeyError as e:
        st.error(f"❌ CSV 컬럼 구조에 문제가 있습니다.\n\n{e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 데이터를 불러오는 중 오류가 발생했습니다.\n\n{e}")
        st.stop()

    st.caption("현재 CSV 컬럼: " + ", ".join(df.columns.astype(str)))

    # 직무 선택
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

    # 필터링
    filtered_df = filter_by_category(df, selected_category)

    st.subheader("2️⃣ 선택한 분야 상위 키워드")

    if filtered_df.empty:
        st.warning("해당 분야에 대한 데이터가 없습니다. CSV 내용을 다시 확인해 주세요.")
    else:
        view_cols = ["word", "count", "total_posts"]
        if "ratio" in filtered_df.columns:
            view_cols.append("ratio")

        st.dataframe(
            filtered_df[view_cols],
            use_container_width=True,
        )

        # 상위 10개 막대그래프
        st.subheader("3️⃣ 키워드 빈도 시각화 (상위 10개)")

        top_n = min(10, len(filtered_df))
        chart_df = filtered_df.head(top_n)[["word", "count"]].set_index("word")

        st.bar_chart(chart_df)

    # 원본 전체 보기
    with st.expander("📂 원본 데이터 전체 보기"):
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
