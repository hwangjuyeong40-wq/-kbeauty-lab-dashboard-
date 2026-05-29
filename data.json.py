import pandas as pd
import json
import os
import glob

def build_v1():
    # 현재 폴더에서 .xlsx 또는 .csv 파일을 찾습니다.
    files = glob.glob("*.xlsx") + glob.glob("*.csv")
    
    if not files:
        print("오류: 데이터 파일을 찾을 수 없습니다. 폴더를 확인하세요.")
        return

    # 첫 번째 파일을 타겟으로 설정
    target_file = files[0]
    print(f"파일 발견: {target_file}를 처리합니다.")

    try:
        # 확장자에 따라 읽기 방식 결정
        if target_file.endswith('.xlsx'):
            df = pd.read_excel(target_file)
        else:
            # CSV일 경우 인코딩 자동 시도
            try:
                df = pd.read_csv(target_file, encoding='utf-8-sig')
            except:
                df = pd.read_csv(target_file, encoding='cp949')

        # 컬럼 공백 제거 및 전처리
        df.columns = [str(col).strip() for col in df.columns]
        
        # 필수 컬럼 전처리
        df["sentiment"] = df["sentiment"].astype(str).str.strip()
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

        # JSON 저장
        df.to_json('data.json', orient='records', force_ascii=False, indent=4)
        print(f"성공: {len(df)}건의 데이터를 'data.json'으로 생성했습니다.")

    except Exception as e:
        print(f"변환 오류 발생: {e}")

if __name__ == "__main__":
    build_v1()