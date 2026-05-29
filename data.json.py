import pandas as pd
import json

# 1. 엑셀 데이터 로드
df = pd.read_excel("final_multilingual_dataset_726.xlsx")
df.columns = [str(col).strip() for col in df.columns]

# 2. 파이썬 코드에 있던 전처리 로직 그대로 적용
sentiment_map = {
    "positive": "긍정", "neutral": "중립", "negative": "부정",
    "긍정": "긍정", "중립": "중립", "부정": "부정"
}
df["sentiment"] = df["sentiment"].astype(str).str.strip().map(sentiment_map).fillna("중립")
df["platform"] = df["platform"].astype(str).str.strip()
df["language"] = df["language"].astype(str).str.strip()
df["product"] = df["product"].fillna("제품명 없음").astype(str).str.strip()
df["review"] = df["review"].fillna("").astype(str)
df["issue_type"] = df["issue_type"].fillna("기타").astype(str).str.strip()
df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

PLATFORM_LABELS = {"kbeauty_platform": "네이버 쇼핑", "hwahae": "화해", "xiaohongshu": "샤오홍슈"}
LANGUAGE_LABELS = {"ko": "한국어", "zh": "중국어"}
df["platform_label"] = df["platform"].map(PLATFORM_LABELS).fillna(df["platform"])
df["language_label"] = df["language"].map(LANGUAGE_LABELS).fillna(df["language"])

# 3. 깃허브 대시보드가 읽을 수 있도록 JSON 파일로 추출
data_list = df[["product", "platform_label", "language_label", "rating", "sentiment", "review", "issue_type"]].to_dict(orient="records")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4)

print("data.json 파일 생성 완료!")