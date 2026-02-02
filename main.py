import db_setup
from scrapers.hankyung_scraper import HankyungScraper

def main():
    db_path = 'expert_alpha_v4.db'
    # 1. DB 초기화 (기존 데이터 유지하고 싶으면 init_db 내부를 수정하되, 일단은 초기화로 갑니다)
    db_setup.init_db(db_path)
    
    # 2. 한경 컨센서스 (무조건 50페이지 긁기 - 노가다는 로봇이 합니다)
    hk = HankyungScraper(db_path)
    try:
        hk.fetch_data(pages=50)
    except Exception as e:
        print(f"❌ 수집 중단됨: {e}")
    
    print("🏁 인간 지표 원재료 수집 완료.")

if __name__ == "__main__":
    main()
