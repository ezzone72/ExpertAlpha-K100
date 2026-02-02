import sqlite3
import requests
import re
import time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=10):
        print(f"📡 네이버 정밀 수집 가동...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            try:
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('table.type_1 tr')
                
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # 1. 제목 및 종목코드 파싱
                    title_a = cols[0].select_one('a')
                    title = title_a.text.strip() if title_a else cols[0].text.strip()
                    
                    stock_code = ""
                    if title_a and 'href' in title_a.attrs:
                        code_match = re.search(r'itemCode=(\d{6})', title_a['href'])
                        stock_code = code_match.group(1) if code_match else ""

                    # 2. 전문가, 증권사, 날짜 보정
                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    raw_date = cols[4].text.strip()
                    # 24.12.15 -> 2024-12-15 형식으로 변환
                    date = f"20{raw_date.replace('.', '-')}" if len(raw_date.strip()) == 8 else raw_date.replace('.', '-')

                    # 3. 제목에서 목표가(숫자) 추출
                    target_price = 0
                    price_match = re.search(r'(\d{1,3}(,\d{3})+)', title)
                    if price_match:
                        target_price = int(price_match.group(1).replace(',', ''))

                    # 💡 핵심: 저장할 칸 이름을 하나하나 지정해서 순서 꼬임을 방지합니다.
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date, stock_code, target_price) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, expert, source, date, stock_code, target_price))
                
                conn.commit()
                print(f"📄 네이버 {page}p 완료")
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ {page}p 에러: {e}")
                break
        conn.close()
