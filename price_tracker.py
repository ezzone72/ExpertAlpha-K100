import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
import os

def track_performance():
    # 1. DB 연결 (루트 경로에 있는 db 파일)
    db_path = 'expert_alpha_v4.db'
    if not os.path.exists(db_path):
        print(f"❌ DB 파일을 찾을 수 없습니다: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM expert_predictions", conn)
    
    current_prices = []
    achievements = []

    print(f"🚀 [ExpertAlpha-K100] 시세 추적 시작 (기준일: {datetime.now().strftime('%Y-%m-%d')})")

    for index, row in df.iterrows():
        # 종목코드 처리 (KOSPI는 ^KS11, 나머지는 .KS)
        ticker_symbol = "^KS11" if row['stock_name'].upper() == 'KOSPI' else f"{row['stock_code']}.KS"
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            # 최근 5일치 데이터를 가져와 마지막 종가 선택 (휴일 대비)
            hist = ticker.history(period='5d')
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                achievement = (current_price / row['target_price']) * 100
            else:
                current_price, achievement = 0, 0
        except Exception as e:
            print(f"⚠️ {row['stock_name']} 시세 로드 실패: {e}")
            current_price, achievement = 0, 0
        
        current_prices.append(round(current_price, 2))
        achievements.append(round(achievement, 2))

    # 데이터 정리
    df['current_price'] = current_prices
    df['achievement_rate'] = achievements
    
    # 2. 콘솔 출력 (로그 확인용)
    print("\n" + "="*80)
    print(df[['date', 'expert_name', 'stock_name', 'target_price', 'current_price', 'achievement_rate']])
    print("="*80)
    
    # 3. CSV 파일로 성적표 누적 보관 (기록용)
    report_name = 'expert_score_board.csv'
    df.to_csv(report_name, index=False, encoding='utf-8-sig')
    print(f"✅ 성적표 업데이트 완료: {report_name}")
    
    conn.close()

if __name__ == "__main__":
    track_performance()
