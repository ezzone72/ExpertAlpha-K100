import sqlite3
import pandas as pd
import yfinance as yf # 주가 수집용 라이브러리
from datetime import datetime, timedelta

def update_prices():
    conn = sqlite3.connect('expert_alpha_v3.db')
    cur = conn.cursor()
    
    # 1. DB에 등록된 종목 코드 가져오기
    cur.execute("SELECT stock_name, stock_code FROM stocks")
    stocks = cur.fetchall()
    
    if not stocks:
        print("⚠️ 등록된 종목이 없습니다. 스크래퍼를 먼저 실행하세요.")
        return

    print(f"📈 {len(stocks)}개 종목의 주가 데이터 수집 시작...")

    for name, code in stocks:
        # 야후 파이낸스용 코드 변환 (예: 005930 -> 005930.KS)
        ticker = f"{code}.KS"
        
        # 최근 1개월치 데이터 가져오기 (성적 계산용)
        data = yf.download(ticker, start="2025-01-01", end="2026-02-02", progress=False)
        
        for date, row in data.iterrows():
            clean_date = date.strftime('%Y-%m-%d')
            close_price = int(row['Close'])
            
            # 주가 저장 (KOSPI 지수는 일단 2500점으로 가상 세팅, 나중에 정밀 수집)
            cur.execute("""
                INSERT OR IGNORE INTO stock_prices (stock_code, date, close_price, kospi_index)
                VALUES (?, ?, ?, ?)
            """, (code, clean_date, close_price, 2500.0))
            
    conn.commit()
    conn.close()
    print("✅ 주가 데이터 동기화 완료!")

if __name__ == "__main__":
    update_prices()
