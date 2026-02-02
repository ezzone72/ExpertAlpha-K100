import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=10):
        print(f"📡 네이버 정밀 수집 시작 (칸 맞춤 버전)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
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
                    
                    title_a = cols[0].select_one('a')
                    title = title_a.text.strip() if title_a else cols[0].text.strip()
                    
                    stock_code = ""
                    if title_a and 'href' in title_a.attrs:
                        code_search = re.search(r'itemCode=(\d{6})', title_a['href'])
                        stock_code = code_search.group(1) if code_search else ""

                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    raw_date = cols[4].text.strip()
                    # 날짜 형식 보정 (24.12.15 -> 2024-12-15)
                    date = f"20{raw_date.replace('.', '-')}" if len(raw_date.strip()) == 8 else raw_date.replace('.', '-')

                    target_price = 0
                    price_match = re.search(r'(\d{1,3}(,\d{3})+)', title)
                    if price_match:
                        target_price = int(price_match.group(1).replace(',', ''))

                    # 🔥 [핵심 수정] INSERT 할 컬럼명을 명시적으로 지정합니다.
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date, stock_code, target_price) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, expert, source, date, stock_code, target_price))
                    new_count += 1
                
                conn.commit()
                print(f"📄 네이버 {page}p 완료")
                time.sleep(0.3)
            except Exception as e:
                print(f"❌ 에러: {e}")
                break
        conn.close()
