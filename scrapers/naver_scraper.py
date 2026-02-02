import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=10):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table.type_1 tr')
            
            for row in rows:
                cols = row.select('td')
                if len(cols) < 5: continue
                
                title = cols[0].text.strip()
                expert = cols[1].text.strip()
                source = cols[2].text.strip()
                # 날짜 교정 (24.12.15 -> 2024-12-15)
                raw_date = cols[4].text.strip()
                date = f"20{raw_date.replace('.', '-')}" if len(raw_date) == 8 else raw_date.replace('.', '-')
                
                # 💡 INSERT 할 때 칸 이름을 하나하나 지정 (절대 안 꼬임)
                cur.execute('''
                    INSERT INTO reports (report_date, title, expert_name, source, target_price) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, title, expert, source, 0))
            conn.commit()
            time.sleep(0.3)
        conn.close()
