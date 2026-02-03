# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
import os

def track_performance():
    db_path = 'expert_alpha_v4.db'
    if not os.path.exists(db_path):
        print("❌ DB 파일을 찾을 수 없습니다.")
        return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM expert_predictions", conn)
    
    # 1. 열 이름 자동 탐지 로직 (소장님 DB 맞춤형)
    cols = df.columns
    name_col = next((c for c in cols if 'name' in c.lower() or '종목' in c), 'stock_name')
    price_col = next((c for c in cols if 'target' in c.lower() or '목표' in c), 'target_price')
    code_col = next((c for c in cols if 'code' in c.lower() or '코드' in c), 'stock_code')

    print(f"🔍 탐지된 열 이름: 종목명({name_col}), 목표가({price_col})")

    current_prices = []
    achievements = []

    for index, row in df.iterrows():
        s_name = str(row[name_col])
        # 목표가가 숫자가 아닐 경우를 대비한 예외처리
        try:
            t_price = float(row[price_col])
        except:
            t_price = 0
            
        s_code = str(row[code_col]) if code_col in row else ""

        # 티커 설정
        if 'KOSPI' in s_name.upper():
            ticker_symbol = "^KS11"
        else:
            ticker_symbol = f"{s_code.strip()}.KS" if s_code and s_code != 'None' else f"{s_name}.KS"

        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='5d')
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            achievement = (current_price / t_price) * 100 if t_price > 0 and current_price > 0 else 0
        except:
            current_price, achievement = 0, 0
        
        current_prices.append(round(current_price, 2))
        achievements.append(round(achievement, 2))

    df['현재가'] = current_prices
    df['달성률(%)'] = achievements
    
    # 최종 결과 저장 (한글 깨짐 방지 utf-8-sig)
    df.to_csv('expert_score_board.csv', index=False, encoding='utf-8-sig')
    print("✅ [ExpertAlpha-K100] 성적표 업데이트 완료!")
    conn.close()

if __name__ == "__main__":
    track_performance()
