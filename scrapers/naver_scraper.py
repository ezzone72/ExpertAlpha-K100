import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        print(f"📡 네이버 금융 리포트 [실전 분석형] 수집 시작...")
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
                    
                    # 1. 제목 및 종목코드 추출
                    title_a = cols[0].select_one('a')
                    title = title_a.text.strip() if title_a else cols[0].text.strip()
                    
                    # 💡 종목코드 추출 (링크 내 itemCode 파라미터 활용)
                    stock_code = ""
                    if title_a and 'href' in title_a.attrs:
                        code_search = re.search(r'itemCode=(\d{6})', title_a['href'])
                        stock_code = code_search.group(1) if code_search else ""

                    # 2. 목표가 추출 (제목에서 '00,000원' 형태를 찾아냄)
                    target_price = 0
                    price_match = re.search(r'(\d{1,3}(,\d{3})+)', title)
                    if price_match:
                        target_price = int(price_match.group(1).replace(',', ''))

                    # 3. 전문가, 증권사, 날짜 (날짜 버그 완전 박멸)
                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    raw_date = cols[4].text.strip()
                    date = f"20{raw_date.replace('.', '-')}" if len(raw_date) == 8 else raw_date.replace('.', '-')

                    # 4. 중복 체크 후 저장
                    cur.execute("SELECT id FROM reports WHERE title=? AND report_date=?", (title, date))
                    if cur.fetchone(): continue
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date, stock_code, target_price) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, expert, source, date, stock_code, target_price))
                    new_count += 1
                
                conn.commit()
                print(f"📄 네이버 {page}p: {new_count}개 누적 (Code: {stock_code}, Price: {target_price})")
                time.sleep(0.3)
            except: break
        conn.close()
