import argparse
import datetime
import pytz
import sqlite3
import pandas as pd
import os
import sys

# 1. 파일명 충돌 및 경로 해결 (db_setup.py 및 하위 폴더 인식)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import db_setup as database  # 이름을 바꾼 db_setup.py를 가져옵니다.

# 2. 하위 모듈 임포트
try:
    from database.fetch_stock_prices import update_prices
except ImportError:
    # 깃허브 액션 및 다양한 환경 대응을 위한 경로 강제 추가
    sys.path.append(os.path.join(os.getcwd(), 'database'))
    from fetch_stock_prices import update_prices

from scrapers.naver_scraper import NaverScraper
from scrapers.hankyung_scraper import HankyungScraper
from analysis.history_manager import HistoryManager

def get_target_info():
    """현재 시간을 기준으로 수집 모드 결정"""
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(seoul_tz)
    
    # 밤 11시(23시)에 실행될 때를 '야간 정밀 수집'으로 정의
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
    # 주가 업데이트 여부 옵션 (기본값 True로 설정하여 수동 실행 시에도 주가 수집)
    parser.add_argument('--update-prices', action='store_false', help="주가 업데이트를 건너뛰려면 사용")
    args = parser.parse_args()

    target_date, mode_msg = get_target_info()
    db_path = 'expert_alpha_v3.db'

    print(f"\n🚀 [ExpertAlpha-K100 v3.0] 시스템 가동")
    print(f"{mode_msg}")
    print("-" * 50)

    # [🔥 필수 1순위] DB 인프라(테이블)부터 생성
    # 이 작업이 먼저 완료되어야 'no such table' 에러가 발생하지 않습니다.
    print("🏗️ 1단계: DB 인프라 초기화 중...")
    database.init_db(db_path=db_path) 

    # [2순위] 주가 데이터 업데이트 (stocks 테이블 채우기)
    # --update-prices 옵션이 꺼져있지 않다면 실행
    print("📊 2단계: 주가 데이터 및 종목 정보 업데이트 중...")
    try:
        update_prices()
    except Exception as e:
        print(f"⚠️ 주가 업데이트 중 오류 발생(무시하고 진행): {e}")

    # [3순위] 리포트 수집 (지능형 스크래퍼 가동)
    print(f"📡 3단계: 리포트 수집 시작 ({target_date})...")
    
    # 네이버 수집 (대량 수집을 위해 pages=100 설정)
    naver = NaverScraper(db_path=db_path)
    naver.fetch_data(pages=50)

    # 한경 수집 (대량 수집을 위해 pages=100 설정)
    hankyung = HankyungScraper(db_path=db_path)
    hankyung.fetch_data(pages=50)

    # [4순위] 전문가 성적 기록 및 분석
    print("📈 4단계: 전문가 성적 계산 및 히스토리 기록 중...")
    try:
        history = HistoryManager(db_path=db_path)
        history.record_daily_scores()
    except Exception as e:
        print(f"⚠️ 성적 기록 중 오류 발생(무시하고 진행): {e}")

    print("-" * 50)
    print(f"🏁 [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 모든 작업 완료!")

if __name__ == "__main__":
    main()
