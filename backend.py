# backend/data_service.py
import os
import pandas as pd

# 프로젝트 기준 BASE_DIR (backend 폴더의 상위 = 프로젝트 루트)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_NAME = "직무별_단순빈도_TOP10(final).csv"
CSV_PATH = os.path.join(DATA_DIR, CSV_NAME)


def load_keyword_data():
    """
    직무별_단순빈도_TOP10(final).csv 파일을 읽어서 DataFrame으로 반환.
    인코딩 문제 대비: utf-8-sig → cp949 순으로 시도.
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


def get_categories(df):
    """
    category 컬럼에서 선택 가능한 직무 목록 가져오기.
    """
    return sorted(df["category"].dropna().unique().tolist())


def filter_by_category(df, category_value: str):
    """
    선택한 category(직무) 기준으로 데이터 필터링.
    """
    filtered = df[df["category"] == category_value].copy()
    # 상위 count 순으로 정렬
    filtered = filtered.sort_values("count", ascending=False).reset_index(drop=True)
    # 비율 컬럼 추가 (선택)
    if "total_posts" in filtered.columns:
        filtered["ratio"] = filtered["count"] / filtered["total_posts"]
    return filtered
