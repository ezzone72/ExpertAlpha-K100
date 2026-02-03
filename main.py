import db_setup
from scrapers.naver_scraper import NaverScraper
import FinanceDataReader as fdr  # <-- 시세 수집용 추가
import sqlite3

def jeban_market_tracker(db_path):
    """[제반장 추가] 전문가가 언급한 종목들만 골라 시세 채우기"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. 일별 시세 테이블 없으면 생성
    cur.execute('''CREATE TABLE IF NOT EXISTS daily_market_data 
                   (trade_date TEXT, stock_code TEXT, stock_name TEXT, close_price REAL, 
                    PRIMARY KEY (trade_date, stock_code))''')
    
    # 2. expert_predictions에 있는 종목 리스트 확인
    cur.execute("SELECT DISTINCT stock_code, stock_name, predict_date FROM expert_predictions")
    targets = cur.fetchall()
    
    print(f"📊 추적 대상 종목: {len(targets)}개 분석 시작...")
    
    for code, name, start_date in targets:
        try:
            # 발표일(start_date)부터 오늘까지의 시세 긁어오기
            # 지수(KOSPI)는 KS11, 일반종목은 코드 그대로 사용
            ticker = 'KS11' if name == 'KOSPI' else code
            df = fdr.DataReader(ticker, start_date)
            
            for date, row in df.iterrows():
                cur.execute('''INSERT OR REPLACE INTO daily_market_data 
                               VALUES (?, ?, ?, ?)''', 
                            (date.strftime('%Y-%m-%d'), code, name, row['Close']))
        except Exception as e:
            print(f"⚠️ {name}({code}) 시세 수집 실패: {e}")
            continue
            
    conn.commit()
    conn.close()
    print("✅ [제반장] 모든 타겟 종목 시세 동기화 완료.")

def main():
    db_path = 'expert_alpha_v4.db'
    db_setup.init_db(db_path)
    
    # 1. 네이버  scraper 가동 (수백 개 긁어오기)
    nv = NaverScraper(db_path)
    nv.fetch_data(pages=50) 
    print("🏁 [긴급] 네이버 수집 공정 완료.")
    
    # 2. [추가] 긁어온 종목들 실제 주가 추적하기
    jeban_market_tracker(db_path)

if __name__ == "__main__":
    main()
