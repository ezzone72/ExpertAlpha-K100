import db_setup
from scrapers.naver_scraper import NaverScraper

def main():
    db_path = 'expert_alpha_v3.db'
    
    # 1. DB 초기화 (새 구조로 생성)
    print("🏗️ DB 초기화 중...")
    db_setup.init_db(db_path)
    
    # 2. 네이버 수집
    print("📡 네이버 수집 시작...")
    naver = NaverScraper(db_path)
    naver.fetch_data(pages=10)
    
    print("✅ 모든 작업 완료!")

if __name__ == "__main__":
    main()
