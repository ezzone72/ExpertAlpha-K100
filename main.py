import database
from scrapers.naver_scraper import NaverScraper
from scrapers.hankyung_scraper import HankyungScraper
from analysis.history_manager import HistoryManager
import sqlite3
import pandas as pd

def main():
    print("🚀 [ExpertAlpha-K100 v3.0] 시스템 가동...")

    # 1. DB 초기화 (테이블이 없으면 생성)
    database.init_db()

    # 2. 네이버 정밀 수집 (10페이지 테스트)
    naver = NaverScraper(db_path='expert_alpha_v3.db')
    naver.fetch_data(pages=10)

    # 3. 한경 정밀 수집 (5페이지 테스트)
    hankyung = HankyungScraper(db_path='expert_alpha_v3.db')
    hankyung.fetch_data(pages=5)

    # 4. 일일 성적 히스토리 기록
    history = HistoryManager(db_path='expert_alpha_v3.db')
    history.record_daily_scores()

    # 5. 결과 확인 (오늘 기록된 상위 5명 리포트)
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
            print("데이터를 분석 중입니다. (주가 데이터와의 매칭 시간이 필요할 수 있습니다)")
        else:
            print(df)
    except:
        print("결과 출력 중 오류 발생 (데이터 적재 중)")
    finally:
        conn.close()

    print("\n🏁 모든 작업이 완료되었습니다. 히스토리가 기록되었습니다.")

if __name__ == "__main__":
    main()
