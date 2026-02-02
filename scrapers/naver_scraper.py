import sqlite3
import requests
from bs4 import BeautifulSoup
import time

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def is_already_exists(self, title, date, expert_name):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM reports WHERE title = ? AND report_date = ? AND expert_name = ?", (title, date, expert_name))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    def fetch_data(self, pages=10):
        print(f"📡 네이버 금융 리포트 강제 수집 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table.type_1 tr')
            
            page_new_count = 0
            for row in rows:
                cols = row.select('td')
                if len(cols) < 5: continue
                
                title = cols[0].text.strip()
                expert_name = cols[1].text.strip()
                source = cols[2].text.strip()
                date = "20" + cols[4].text.strip().replace('.', '-')
                
                if self.is_already_exists(title, date, expert_name):
                    continue # 중복이면 다음 리스트로 넘어가고 멈추지는 않음
                
                cur.execute('''
                    INSERT INTO reports (title, expert_name, source, report_date)
                    VALUES (?, ?, ?, ?)
                ''', (title, expert_name, source, date))
                page_new_count += 1
                new_count += 1
            
            conn.commit()
            print(f"📄 네이버 {page}페이지 완료: {page_new_count}개 신규 추가")
            time.sleep(0.3)

        conn.close()
        print(f"✅ 네이버 총 {new_count}개 DB 저장 완료!")
