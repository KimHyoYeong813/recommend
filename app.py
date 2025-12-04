# app.py
import streamlit as st
import pandas as pd

from backend.backend import load_keyword_data, get_categories, filter_by_category




@st.cache_data
def get_data():
    """
    Streamlit 캐시를 이용해 데이터 한 번만 로드.
    """
    df = load_keyword_data()
    return df


def main():
    st.set_page_config(
        page_title="AI 역량 키워드 뷰어",
        layout="wide",
    )

    st.title("📊 분야별 자주 요구되는 AI 역량 키워드")

    # 1) 데이터 로드
    try:
        df = get_data()
    except FileNotFoundError as e:
        st.error(f"❌ 데이터 파일을 찾을 수 없습니다.\n\n{e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 데이터를 불러오는 중 오류가 발생했습니다.\n\n{e}")
        st.stop()

    # 컬럼 구조 안내
    st.caption("현재 CSV 컬럼: " + ", ".join(df.columns.astype(str)))

    # 2) 직무(category) 선택 UI
    st.subheader("1️⃣ 관심 있는 직무 선택")

    categories = get_categories(df)

    if not categories:
        st.error("category 컬럼에 값이 없습니다. CSV 데이터를 확인해 주세요.")
        st.stop()

    default_index = 0
    selected_category = st.selectbox(
        "관심 있는 직무(분야)를 선택하세요:",
        options=categories,
        index=default_index,
    )

    st.write(f"### 선택한 분야: **{selected_category}**")

    # 3) 선택한 직무 기준 필터링
    filtered_df = filter_by_category(df, selected_category)

    st.subheader("2️⃣ 선택한 분야 상위 키워드")

    if filtered_df.empty:
        st.warning("해당 분야에 대한 데이터가 없습니다. CSV 내용을 다시 확인해 주세요.")
    else:
        # 컬럼 일부만 보기용 DataFrame
        view_cols = ["word", "count", "total_posts"]
        if "ratio" in filtered_df.columns:
            view_cols.append("ratio")

        st.dataframe(
            filtered_df[view_cols],
            use_container_width=True,
        )

        # 4) 간단한 bar chart (상위 N개만)
        st.subheader("3️⃣ 키워드 빈도 시각화 (상위 10개)")

        top_n = min(10, len(filtered_df))
        chart_df = filtered_df.head(top_n)[["word", "count"]]

        # 인덱스를 word로 설정해서 plot
        chart_df = chart_df.set_index("word")
        st.bar_chart(chart_df)

    # 5) 전체 데이터 보기 (옵션)
    with st.expander("📂 원본 데이터 전체 보기"):
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
