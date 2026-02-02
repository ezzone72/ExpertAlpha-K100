import argparse
import datetime
import pytz
import sqlite3
import pandas as pd
import os

# 기존 소장님 시스템 모듈 임포트
import database
from scrapers.naver_scraper import NaverScraper
from scrapers.hankyung_scraper import HankyungScraper
from analysis.history_manager import HistoryManager
from database.fetch_stock_prices import update_prices

def get_target_info():
    """실행 시간에 따라 수집 대상 날짜와 모드를 결정"""
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(seoul_tz)
    
    # 밤 11:30 ~ 11:59 사이 실행 시: 오늘 날짜
    # 00:00 ~ 새벽 시간 실행 시: 어제 날짜
    if now.hour == 23:
        target_date = now.strftime('%Y-%m-%d')
        mode_msg = f"🌙 [야간 정밀 수집] 오늘({target_date}) 데이터를 마감 기록합니다."
    elif now.hour < 6:
        target_date = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        mode_msg = f"🌅 [새벽 소급 수집] 전일({target_date}) 데이터를 기록합니다."
    else:
        target_date = now.strftime('%Y-%m-%d')
        mode_msg = f"☀️ [일반 수집] 현재 날짜({target_date}) 기준으로 가동합니다."
        
    return target_date, mode_msg

def main():
    # 1. 실행 옵션 설정
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-prices', action='store_true', help='주가 데이터를 새로 수집할지 여부')
    args = parser.parse_args()

    # 2. 날짜 및 모드 확인
    target_date, mode_msg = get_target_info()
    print(f"\n🚀 [ExpertAlpha-K100 v3.0] 시스템 가동")
    print(f"{mode_msg}")
    print("-" * 50)

    # 3. DB 초기화 및 필수 테이블 강제 체크
    database.init_db()
    
    # 4. 주가 수집 (옵션 스위치)
    if args.update_prices:
        print("📊 주가 데이터 및 종목 정보 업데이트 중...")
        update_prices()
    else:
        print("⏩ 주가 업데이트 건너뜀 (기존 데이터 활용)")

    # 5. 전문가 리포트 수집 (세밀하게 긁기 위해 페이지 수 상향 조정)
    # 스케줄러 가동 시에는 더 정밀하게 긁도록 설정 가능
    print(f"📡 {target_date} 리포트 수집 시작 (Naver & Hankyung)...")
    
    db_path = 'expert_alpha_v3.db'
    
    naver = NaverScraper(db_path=db_path)
    naver.fetch_data(pages=10) # 밤에는 넉넉하게 10페이지

    hankyung = HankyungScraper(db_path=db_path)
    hankyung.fetch_data(pages=5)

    # 6. 성적 기록 및 분석
    print("📈 전문가 성적 계산 및 히스토리 업데이트 중...")
    history = HistoryManager(db_path=db_path)
    history.record_daily_scores()

    # 7. 최종 결과 브리핑 (Top 5)
    print(f"\n🏆 {target_date} 기준 실시간 성적 Top 5")
    print("=" * 50)
    conn = sqlite3.connect(db_path)
    report_query = """
    SELECT s.name, s.organization, s.provider, h.avg_alpha, h.total_count
    FROM performance_history h
    JOIN sources s ON h.source_id = s.source_id
    WHERE h.record_date = ?
    ORDER BY h.avg_alpha DESC
    LIMIT 5
    """
    try:
        df = pd.read_sql_query(report_query, conn, params=(target_date,))
        if df.empty:
            print(f"🧐 {target_date}에 계산된 성적이 아직 없습니다.")
            print("   (매칭되는 주가 데이터가 부족하거나 리포트가 없을 수 있습니다.)")
        else:
            print(df)
    except Exception as e:
        print(f"❌ 결과 출력 중 오류: {e}")
    finally:
        conn.close()
    
    print("-" * 50)
    print(f"🏁 [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
