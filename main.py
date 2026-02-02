import argparse # 옵션 조절용 도구
import database
from scrapers.naver_scraper import NaverScraper
from scrapers.hankyung_scraper import HankyungScraper
from analysis.history_manager import HistoryManager
from database.fetch_stock_prices import update_prices # 방금 만든 주가 수집기
import sqlite3
import pandas as pd

def main():
    # 1. 실행 옵션 설정
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-prices', action='store_true', help='주가 데이터를 새로 수집할지 여부')
    args = parser.parse_args()

    print("🚀 [ExpertAlpha-K100 v3.0] 시스템 가동...")

    # 2. DB 초기화
    database.init_db()

    # 3. 주가 수집 (옵션이 켜져 있을 때만!)
    if args.update_prices:
        print("📊 주가 데이터 업데이트 모드 활성화...")
        update_prices()
    else:
        print("⏩ 주가 업데이트를 건너뜁니다. (기존 데이터 사용)")

    # 4. 리포트 수집 (네이버/한경)
    naver = NaverScraper(db_path='expert_alpha_v3.db')
    naver.fetch_data(pages=5)

    hankyung = HankyungScraper(db_path='expert_alpha_v3.db')
    hankyung.fetch_data(pages=3)

    # 5. 성적 기록 및 분석
    history = HistoryManager(db_path='expert_alpha_v3.db')
    history.record_daily_scores()

    # 6. 결과 확인
    print("\n🏆 오늘의 전문가 실력 순위 (Top 5)")
    conn = sqlite3.connect('expert_alpha_v3.db')
    report_query = """
    SELECT s.name, s.organization, s.provider, h.avg_alpha, h.total_count
    FROM performance_history h
    JOIN sources s ON h.source_id = s.source_id
    WHERE h.record_date = date('now')
    ORDER BY h.avg_alpha DESC
    LIMIT 5
    """
    try:
        df = pd.read_sql_query(report_query, conn)
        if df.empty:
            print("🤔 계산된 성적이 아직 없습니다. 주가 데이터가 부족할 수 있습니다.")
        else:
            print(df)
    except:
        print("결과 출력 중 오류 발생")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
