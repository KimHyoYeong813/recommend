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
    count 기준 내림차순 정렬, 인덱스 1부터 설정, word → '요구 역량'으로 변경.
    total_posts는 나중에 캡션으로 쓰기 위해 일단 유지.
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

    # === 직무 카테고리 버튼 UI ===
    st.subheader("1️⃣ 관심 있는 직무 선택")

    categories = get_categories(df)
    if not categories:
        st.error("category 컬럼에 값이 없습니다. CSV 데이터를 확인해 주세요.")
        st.stop()

    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = categories[0]

    st.write("관심 있는 직무(분야)를 클릭하세요:")

    num_cols = 3
    cols = st.columns(num_cols)

    for idx, cat in enumerate(categories):
        col = cols[idx % num_cols]
        if cat == st.session_state["selected_category"]:
            button_label = f"✅ {cat}"
        else:
            button_label = cat

        if col.button(button_label, key=f"cat_btn_{cat}"):
            st.session_state["selected_category"] = cat

    selected_category = st.session_state["selected_category"]
    st.write(f"### 선택한 분야: **{selected_category}**")

    # === 선택한 직무 기준 필터링 ===
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
        # total_posts, ratio 컬럼은 제거
        drop_cols = [c for c in ["total_posts", "ratio"] if c in filtered_df.columns]
        display_df = filtered_df.drop(columns=drop_cols, errors="ignore")

        view_cols = ["요구 역량", "count"]
        display_df = display_df[view_cols]

        st.dataframe(display_df, use_container_width=True)





if __name__ == "__main__":
    main()
