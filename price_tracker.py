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
    df = pd.read_sql_query("SELECT * FROM expert_predictions", conn)
    df.columns = [c.lower() for c in df.columns]

    current_prices = []
    achievements = []

    print(f"🚀 [ExpertAlpha-K100] 시세 추적 시작...")

    for index, row in df.iterrows():
        s_name = row['stock_name']
        t_price = row['target_price']
        s_code = str(row['stock_code']) if 'stock_code' in row else ""

        if 'KOSPI' in s_name.upper():
            ticker_symbol = "^KS11"
        else:
            ticker_symbol = f"{s_code}.KS" if s_code and s_code != "None" else f"{s_name}.KS"

        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='5d')
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            achievement = (current_price / t_price) * 100 if current_price > 0 else 0
        except:
            current_price, achievement = 0, 0
        
        current_prices.append(round(current_price, 2))
        achievements.append(round(achievement, 2))

    df['current_price'] = current_prices
    df['achievement_rate'] = achievements
    
    df.to_csv('expert_score_board.csv', index=False, encoding='utf-8-sig')
    print("✅ 성적표 업데이트 완료!")
    conn.close()

if __name__ == "__main__":
    track_performance()
