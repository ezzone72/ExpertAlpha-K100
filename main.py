import argparse
import datetime
import pytz
import sqlite3
import pandas as pd
import os
import sys

# 1. 파일명 충돌 및 경로 해결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db_setup as database  # 이름을 바꾼 db_setup.py를 가져옵니다.

# 폴더 내 모듈 임포트
try:
    from database.fetch_stock_prices import update_prices
except ImportError:
    # 깃허브 액션 환경 대응
    sys.path.append(os.path.join(os.getcwd(), 'database'))
    from fetch_stock_prices import update_prices

from scrapers.naver_scraper import NaverScraper
from scrapers.hankyung_scraper import HankyungScraper
from analysis.history_manager import HistoryManager

def get_target_info():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(seoul_tz)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-prices', action='store_true')
    args = parser.parse_args()

    target_date, mode_msg = get_target_info()
    print(f"\n🚀 [ExpertAlpha-K100 v3.0] 시스템 가동")
    print(f"{mode_msg}")
    print("-" * 50)

    # [🔥 중요] 1순위: DB와 테이블부터 무조건 만듭니다 (stocks 테이블 생성)
    print("🏗️ DB 인프라 초기화 중...")
    database.init_db() 

    # 2순위: 테이블이 확실히 있을 때 주가를 업데이트합니다.
    if args.update_prices:
        print("📊 주가 데이터 및 종목 정보 업데이트 중...")
        try:
            update_prices()
        except Exception as e:
            print(f"⚠️ 주가 업데이트 중 오류 발생(무시하고 진행): {e}")

    # 3순위: 리포트 수집
    db_path = 'expert_alpha_v3.db'
    print(f"📡 {target_date} 리포트 수집 시작...")
    
    naver = NaverScraper(db_path=db_path)
    naver.fetch_data(pages=100)

    hankyung = HankyungScraper(db_path=db_path)
    hankyung.fetch_data(pages=100)

    # 4순위: 성적 기록
    print("📈 전문가 성적 계산 중...")
    history = HistoryManager(db_path=db_path)
    history.record_daily_scores()

    print(f"🏁 [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 작업 완료!")

if __name__ == "__main__":
    main()
