# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
import os

def track_performance():
    db_path = 'expert_alpha_v4.db'
    if not os.path.exists(db_path):
        print(f"❌ DB 파일을 찾을 수 없습니다: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    # 컬럼명을 확인하기 위해 전체 데이터를 가져옵니다.
    df = pd.read_sql_query("SELECT * FROM expert_predictions", conn)
    
    # DB 컬럼명을 모두 소문자로 바꿔서 매칭 에러를 방지합니다.
    df.columns = [c.lower() for c in df.columns]
    
    # 필수 컬럼 존재 확인 (없으면 에러 대신 안내)
    required = ['stock_name', 'target_price']
    for req in required:
        if req not in df.columns:
            print(f"❌ DB에 '{req}' 컬럼이 없습니다. 현재 컬럼: {df.columns.tolist()}")
            return

    current_prices = []
    achievements = []

    print(f"🚀 [ExpertAlpha-K100] 시세 추적 시작...")

    for index, row in df.iterrows():
        # stock_code가 없으면 종목명으로 대체하는 예외처리
        s_code = str(row['stock_code']) if 'stock_code' in row else ""
        s_name = row['stock_name']
        t_price = row['target_price']

        # 티커 설정
        if 'KOSPI' in s_name.upper():
            ticker_symbol = "^KS11"
        else:
            # 코드가 있으면 코드로, 없으면 이름으로 시도 (보통 코드가 정확합니다)
            ticker_symbol = f"{s_code}.KS" if s_code else s_name

        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='5d')
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                achievement = (current_price / t_price) * 100
            else:
                current_price, achievement = 0, 0
        except Exception as e:
            print(f"⚠️ {s_name} 시세 로드 실패: {e}")
            current_price, achievement = 0, 0
        
        current_prices.append(round(current_price, 2))
        achievements.append(round(achievement, 2))

    df['current_price'] = current_prices
    df['achievement_rate'] = achievements
    
    # 결과 출력 및 CSV 저장
    print("\n" + "="*80)
    print(df)
    print("="*80)
    
    df.to_csv('expert_score_board.csv', index=False, encoding='utf-8-sig')
    print("✅ 성적표(expert_score_board.csv) 업데이트 완료!")
    conn.close()

if __name__ == "__main__":
    track_performance()
