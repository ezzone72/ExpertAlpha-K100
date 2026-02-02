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
        print(f"📡 네이버 금융 리포트 정밀 수집 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for page in range(1, pages + 1):
            # 💡 [핵심] 뒤에 type=invest와 같은 추가 파라미터를 붙여야 페이지 이동이 확실히 작동합니다.
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            
            try:
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('table.type_1 tr')
                
                page_new_count = 0
                valid_row_count = 0

                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    valid_row_count += 1
                    title = cols[0].text.strip()
                    expert_name = cols[1].text.strip()
                    source = cols[2].text.strip()
                    date = "20" + cols[4].text.strip().replace('.', '-')
                    
                    if self.is_already_exists(title, date, expert_name):
                        continue 
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date)
                        VALUES (?, ?, ?, ?)
                    ''', (title, expert_name, source, date))
                    page_new_count += 1
                    new_count += 1
                
                conn.commit()
                # 💡 로그에 현재 페이지의 실제 데이터 제목 하나를 같이 찍어서, 정말 페이지가 바뀌는지 확인합니다.
                first_title = rows[2].select('td')[0].text.strip()[:15] if valid_row_count > 0 else "N/A"
                print(f"📄 네이버 {page}p 완료: {page_new_count}개 추가 (첫제목: {first_title}...)")
                
                time.sleep(0.3)
            except Exception as e:
                print(f"❌ 네이버 {page}p 에러: {e}")
                break

        conn.close()
        print(f"✅ 네이버 총 {new_count}개 수집 완료!")
