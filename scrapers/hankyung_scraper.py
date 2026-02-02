import requests
from bs4 import BeautifulSoup
import sqlite3
import time

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path
        self.provider = "HANKYUNG"

    def fetch_data(self, pages=5):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 한경 컨센서스 종목분석 페이지
        base_url = "http://consensus.hankyung.com/apps.analysis/analysis.list?&sdate=2025-02-03&edate=2026-02-02&search_report_classify=RP_GW&page="
        
        print(f"📡 {self.provider} 수집 시작...")

        for page in range(1, pages + 1):
            url = f"{base_url}{page}"
            resp = requests.get(url, headers=headers)
            # 한경은 인코딩 설정이 중요할 수 있습니다
            resp.encoding = 'euc-kr' 
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 리스트 테이블 행(tr) 추출
            rows = soup.select('div.table_style01 table tbody tr')
            
            for row in rows:
                cols = row.select('td')
                if len(cols) < 6: continue
                
                # 1. 데이터 추출
                # 한경 구조: [0]날짜, [1]제목, [2]적정가, [3]투자의견, [4]작성자, [5]제공출처
                date = cols[0].text.strip().replace('.', '-')
                title = cols[1].select_one('a').text.strip()
                # 제목에서 종목명 추출 (보통 "삼성전자(005930)" 형식)
                raw_title = cols[1].text.strip()
                stock_name = raw_title.split('(')[0].strip() if '(' in raw_title else "Unknown_Stock"
                
                name = cols[4].text.strip() # 작성자 실명
                org = cols[5].text.strip()  # 증권사명

                # 2. DB 저장 (sources)
                cur.execute("""
                    INSERT OR IGNORE INTO sources (name, type, provider, organization)
                    VALUES (?, ?, ?, ?)
                """, (name, 'ANALYST', self.provider, org))
                
                cur.execute("SELECT source_id FROM sources WHERE name = ? AND provider = ?", (name, self.provider))
                source_id = cur.fetchone()[0]
                
                # 3. DB 저장 (statements)
                cur.execute("""
                    INSERT INTO statements (source_id, stock_name, issue_date, title)
                    VALUES (?, ?, ?, ?)
                """, (source_id, stock_name, date, title))

            print(f"   - {self.provider} {page}페이지 완료")
            time.sleep(0.5)

        conn.commit()
        conn.close()
        print(f"🏁 {self.provider} 수집 종료.")

if __name__ == "__main__":
    scraper = HankyungScraper('../expert_alpha_v3.db')
    scraper.fetch_data(5)
