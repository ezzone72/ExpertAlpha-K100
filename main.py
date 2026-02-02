import db_setup
from scrapers.naver_scraper import NaverScraper

def main():
    db_path = 'expert_alpha_v4.db'
    db_setup.init_db(db_path)
    
    # 지금은 한경 대신 확실한 네이버 종목분석만 팹니다.
    nv = NaverScraper(db_path)
    nv.fetch_data(pages=50) # 50페이지 긁으면 수백 개 나옵니다.
    
    print("🏁 [긴급] 네이버 수집 공정 완료.")

if __name__ == "__main__":
    main()
