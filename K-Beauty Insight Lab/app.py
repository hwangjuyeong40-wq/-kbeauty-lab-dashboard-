import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud


DATA_FILE = "final_multilingual_dataset_726.xlsx"

SENTIMENT_ORDER = ["긍정", "중립", "부정"]
SENTIMENT_COLORS = {
    "긍정": "#2563eb",
    "중립": "#16a34a",
    "부정": "#dc2626",
}
PLATFORM_LABELS = {
    "kbeauty_platform": "네이버 쇼핑",
    "hwahae": "화해",
    "xiaohongshu": "샤오홍슈",
}
LANGUAGE_LABELS = {
    "ko": "한국어",
    "zh": "중국어",
}
ISSUE_ORDER = ["배송지연", "통관문제", "정품논란", "오배송", "반품"]


st.set_page_config(
    page_title="K-Beauty Insight Lab",
    page_icon="💄",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE)
    df.columns = [str(col).strip() for col in df.columns]

    sentiment_map = {
        "positive": "긍정",
        "neutral": "중립",
        "negative": "부정",
        "긍정": "긍정",
        "중립": "중립",
        "부정": "부정",
    }
    df["sentiment"] = df["sentiment"].astype(str).str.strip().map(sentiment_map).fillna("중립")
    df["platform"] = df["platform"].astype(str).str.strip()
    df["platform_label"] = df["platform"].map(PLATFORM_LABELS).fillna(df["platform"])
    df["language"] = df["language"].astype(str).str.strip()
    df["language_label"] = df["language"].map(LANGUAGE_LABELS).fillna(df["language"])
    df["product"] = df["product"].fillna("제품명 없음").astype(str).str.strip()
    df["review"] = df["review"].fillna("").astype(str)
    df["issue_type"] = df["issue_type"].fillna("기타").astype(str).str.strip()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    return df


def make_count_df(series: pd.Series, name: str) -> pd.DataFrame:
    count_df = series.value_counts().rename_axis(name).reset_index(name="건수")
    count_df["비율(%)"] = (count_df["건수"] / count_df["건수"].sum() * 100).round(1)
    return count_df


def section_title(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


df = load_data()

st.title("K-Beauty Insight Lab")
st.markdown("#### 한국 소비자 리뷰 기반 K-뷰티 데이터 분석 플랫폼")

total_reviews = len(df)
positive_count = int((df["sentiment"] == "긍정").sum())
neutral_count = int((df["sentiment"] == "중립").sum())
negative_count = int((df["sentiment"] == "부정").sum())

kpi_cols = st.columns(4)
kpi_cols[0].metric("총 리뷰 수", f"{total_reviews:,}건")
kpi_cols[1].metric("긍정 리뷰 수", f"{positive_count:,}건")
kpi_cols[2].metric("중립 리뷰 수", f"{neutral_count:,}건")
kpi_cols[3].metric("부정 리뷰 수", f"{negative_count:,}건")

st.divider()

section_title("데이터 분석", "수집된 K-뷰티 리뷰 데이터의 핵심 분포를 확인합니다.")

sentiment_counts = (
    df["sentiment"]
    .value_counts()
    .reindex(SENTIMENT_ORDER, fill_value=0)
    .rename_axis("감성")
    .reset_index(name="건수")
)
sentiment_counts["비율(%)"] = (
    sentiment_counts["건수"] / max(sentiment_counts["건수"].sum(), 1) * 100
).round(1)

sentiment_col, rating_col = st.columns(2)
with sentiment_col:
    st.markdown("##### 감성 분석")
    fig_sentiment = px.pie(
        sentiment_counts,
        names="감성",
        values="건수",
        color="감성",
        color_discrete_map=SENTIMENT_COLORS,
        hole=0.35,
    )
    fig_sentiment.update_traces(textinfo="label+percent+value")
    fig_sentiment.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
    st.plotly_chart(fig_sentiment, use_container_width=True)
    st.dataframe(sentiment_counts, use_container_width=True, hide_index=True)

with rating_col:
    st.markdown("##### 별점 분석")
    rating_counts = (
        df.dropna(subset=["rating"])
        .assign(rating=lambda data: data["rating"].astype(int))
        .query("rating >= 1 and rating <= 5")
        .groupby("rating", as_index=False)
        .size()
        .rename(columns={"rating": "별점", "size": "건수"})
    )
    rating_counts = (
        pd.DataFrame({"별점": range(1, 6)})
        .merge(rating_counts, on="별점", how="left")
        .fillna({"건수": 0})
    )
    fig_rating = px.bar(rating_counts, x="별점", y="건수", text="건수", color_discrete_sequence=["#7c3aed"])
    fig_rating.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(dtick=1))
    st.plotly_chart(fig_rating, use_container_width=True)

product_col, platform_col = st.columns(2)
with product_col:
    st.markdown("##### 제품별 분석")
    product_counts = make_count_df(df["product"], "제품명").head(10)
    fig_product = px.bar(
        product_counts.sort_values("건수"),
        x="건수",
        y="제품명",
        orientation="h",
        text="건수",
        color_discrete_sequence=["#0ea5e9"],
    )
    fig_product.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title="")
    st.plotly_chart(fig_product, use_container_width=True)

with platform_col:
    st.markdown("##### 플랫폼 분석")
    platform_counts = make_count_df(df["platform_label"], "플랫폼")
    fig_platform = px.bar(platform_counts, x="플랫폼", y="건수", text="건수", color_discrete_sequence=["#f97316"])
    fig_platform.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title="")
    st.plotly_chart(fig_platform, use_container_width=True)

language_col, issue_col = st.columns(2)
with language_col:
    st.markdown("##### 언어 분석")
    language_counts = make_count_df(df["language_label"], "언어")
    fig_language = px.bar(language_counts, x="언어", y="비율(%)", text="비율(%)", color_discrete_sequence=["#14b8a6"])
    fig_language.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title="비율(%)")
    st.plotly_chart(fig_language, use_container_width=True)
    st.dataframe(language_counts, use_container_width=True, hide_index=True)

with issue_col:
    st.markdown("##### Issue 분석")
    issue_counts = (
        df["issue_type"]
        .value_counts()
        .reindex(ISSUE_ORDER, fill_value=0)
        .rename_axis("issue_type")
        .reset_index(name="건수")
    )
    fig_issue = px.bar(issue_counts, x="issue_type", y="건수", text="건수", color_discrete_sequence=["#ef4444"])
    fig_issue.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title="")
    st.plotly_chart(fig_issue, use_container_width=True)

st.divider()

section_title("리뷰 검색", "검색 결과는 최대 10건만 표시합니다.")
keyword = st.text_input("검색어", placeholder="촉촉, 발림성, 흡수력, 진정, 순함, 재구매")

if keyword.strip():
    pattern = re.escape(keyword.strip())
    search_results = df[df["review"].str.contains(pattern, case=False, na=False)].head(10)
    display_cols = ["product", "rating", "sentiment", "review"]
    st.dataframe(
        search_results[display_cols].rename(
            columns={
                "product": "제품명",
                "rating": "별점",
                "sentiment": "감성",
                "review": "리뷰 원문",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("검색어를 입력하면 관련 리뷰를 최대 10건까지 확인할 수 있습니다.")

st.divider()

section_title("감성별 원본 데이터 보기", "각 감성별 리뷰를 최대 20건씩 표시합니다.")
positive_tab, neutral_tab, negative_tab = st.tabs(["긍정", "중립", "부정"])
tab_map = {
    positive_tab: "긍정",
    neutral_tab: "중립",
    negative_tab: "부정",
}
for tab, sentiment in tab_map.items():
    with tab:
        review_subset = df[df["sentiment"] == sentiment][
            ["product", "platform_label", "language_label", "rating", "review"]
        ].head(20)
        st.dataframe(
            review_subset.rename(
                columns={
                    "product": "제품명",
                    "platform_label": "플랫폼",
                    "language_label": "언어",
                    "rating": "별점",
                    "review": "리뷰 원문",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

st.divider()

section_title("워드클라우드", "한국어 리뷰(language == 'ko')만 사용합니다.")
ko_text = " ".join(df.loc[df["language"] == "ko", "review"].dropna().astype(str).head(396))

if ko_text.strip():
    font_candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path = next((path for path in font_candidates if pd.io.common.file_exists(path)), None)
    wordcloud = WordCloud(
        width=1000,
        height=420,
        background_color="white",
        font_path=font_path,
        max_words=120,
        colormap="viridis",
    ).generate(ko_text)

    fig_wc, ax = plt.subplots(figsize=(10, 4.2))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc, clear_figure=True)
else:
    st.warning("한국어 리뷰 데이터가 없어 워드클라우드를 생성할 수 없습니다.")

st.divider()

with st.expander("V2 확장 계획"):
    st.markdown(
        """
        - Frontend: Next.js, TypeScript, Tailwind CSS
        - Backend: FastAPI
        - Database: PostgreSQL, Supabase
        - Deployment: Vercel, Render
        - 기능: 실시간 리뷰 검색, 네이버 쇼핑 리뷰 수집, 평균 별점/긍정률/부정률 분석, AI 추천 시스템
        """
    )

