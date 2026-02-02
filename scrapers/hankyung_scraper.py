import sqlite3
import requests
from bs4 import BeautifulSoup
import time

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def is_already_exists(self, title, date, expert_name):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM reports WHERE title = ? AND report_date = ? AND expert_name = ?", (title, date, expert_name))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    def fetch_data(self, pages=5):
        print(f"📡 한경 컨센서스 수집 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        
        for page in range(1, pages + 1):
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock&pagenum=20&page={page}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('div.table_main table tbody tr')
            
            duplicate_in_page = 0
            page_items = 0

            for row in rows:
                cols = row.select('td')
                if len(cols) < 6: continue
                
                page_items += 1
                date = cols[0].text.strip()
                title = cols[2].text.strip()
                expert_name = cols[3].text.strip()
                source = cols[4].text.strip()
                
                if self.is_already_exists(title, date, expert_name):
                    duplicate_in_page += 1
                    continue
                
                # 🔥 데이터 담기 (INSERT)
                cur.execute('''
                    INSERT INTO reports (title, expert_name, source, report_date)
                    VALUES (?, ?, ?, ?)
                ''', (title, expert_name, source, date))
                new_count += 1
            
            # 🔥 결제 확정 (COMMIT)
            conn.commit()
            print(f"📄 한경 {page}페이지 완료: {page_items - duplicate_in_page}개 신규 수집")
            
            if page_items > 0 and duplicate_in_page == page_items:
                print(f"🛑 중복 데이터 발견. 한경 수집을 조기 종료합니다.")
                break
            time.sleep(0.3)

        conn.close()
        print(f"✅ 한경 총 {new_count}개 DB 저장 완료!")
