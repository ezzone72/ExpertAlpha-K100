import db_setup
from scrapers.hankyung_scraper import HankyungScraper
from scrapers.naver_scraper import NaverScraper

def main():
    db_path = 'expert_alpha_v4.db'
    db_setup.init_db(db_path) # 새로 깨끗하게 시작
    
    # 1. 한경 컨센서스 수집 (50페이지)
    hk = HankyungScraper(db_path)
    hk.fetch_data(pages=50)
    
    # 2. 네이버 종목분석 수집 (30페이지)
    nv = NaverScraper(db_path)
    nv.fetch_data(pages=30)
    
    print("🏁 [종합] 한경과 네이버에서 모든 원재료를 확보했습니다.")

if __name__ == "__main__":
    main()
