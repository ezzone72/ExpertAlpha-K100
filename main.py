import db_setup
from scrapers.hankyung_scraper import HankyungScraper

def main():
    db_path = 'expert_alpha_v4.db'
    db_setup.init_db(db_path)
    
    # 이제 네이버는 잠시 쉬고, 확실한 한경 데이터부터 쌓습니다.
    hk = HankyungScraper(db_path)
    hk.fetch_data(pages=10) # 10페이지면 최근 200개 종목 리포트입니다.
    
    print("🏁 [완료] 근거 중심의 데이터 수집이 끝났습니다.")

if __name__ == "__main__":
    main()
