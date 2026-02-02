import requests
from bs4 import BeautifulSoup
import sqlite3
import time

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path
        self.provider = "NAVER"

    def fetch_data(self, pages=10):
        # DB 연결 (상위 폴더에 있는 db파일을 찾아가야 하므로 경로 주의)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        print(f"📡 {self.provider} 정밀 수집 시작 (실명 추출 모드)...")

        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 리스트 테이블 행 추출
            rows = soup.select('table.type_1 tr')
            for row in rows:
                cols = row.select('td')
                if len(cols) < 5: continue
                
                # 데이터 파싱
                stock_name = cols[0].text.strip()
                title = cols[1].text.strip()
                
                # [중요] 작성자 정보 정밀 분리 (증권사 | 이름)
                author_raw = cols[2].text.strip()
                if '|' in author_raw:
                    org, name = [x.strip() for x in author_raw.split('|')]
                else:
                    org = author_raw
                    name = "Unknown" # 실명이 없을 경우

                date = "20" + cols[4].text.strip().replace('.', '-') # 26.02.02 -> 2026-02-02

                # 1. 출처(sources) 테이블 저장
                cur.execute("""
                    INSERT OR IGNORE INTO sources (name, type, provider, organization)
                    VALUES (?, ?, ?, ?)
                """, (name, 'ANALYST', self.provider, org))
                
                # 저장된 source_id 가져오기
                cur.execute("SELECT source_id FROM sources WHERE name = ? AND provider = ?", (name, self.provider))
                res = cur.fetchone()
                if res:
                    source_id = res[0]
                    
                    # 2. 발언(statements) 테이블 저장
                    cur.execute("""
                        INSERT INTO statements (source_id, stock_name, issue_date, title)
                        VALUES (?, ?, ?, ?)
                    """, (source_id, stock_name, date, title))

            print(f"   - {self.provider} {page}페이지 완료")
            time.sleep(0.3)

        conn.commit()
        conn.close()
        print(f"🏁 {self.provider} 수집 종료.")

if __name__ == "__main__":
    # 단독 실행 테스트용 (경로는 프로젝트 루트 기준)
    scraper = NaverScraper('../expert_alpha_v3.db')
    scraper.fetch_data(5)
