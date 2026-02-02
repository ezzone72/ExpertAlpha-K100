import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=20): # 페이지를 좀 더 넉넉히 훑습니다.
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
                    
                    title_a = cols[0].select_one('a')
                    full_title = title_a.text.strip() if title_a else cols[0].text.strip()
                    
                    # 💡 종목명 및 코드 정밀 추출 (예: "삼성전자(005930)")
                    stock_name, stock_code = "", ""
                    name_code_match = re.search(r'(.+?)\((\d{6})\)', full_title)
                    if name_code_match:
                        stock_name = name_code_match.group(1).strip()
                        stock_code = name_code_match.group(2).strip()
                    elif title_a and 'href' in title_a.attrs: # 제목에 없으면 링크에서 코드라도 추출
                        code_match = re.search(r'itemCode=(\d{6})', title_a['href'])
                        stock_code = code_match.group(1) if code_match else ""

                    # 전문가, 증권사, 날짜 (YYYY-MM-DD)
                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    raw_date = cols[4].text.strip()
                    report_date = f"20{raw_date.replace('.', '-')}" if len(raw_date) == 8 else raw_date.replace('.', '-')

                    # 목표가 추출 (숫자만 남기기)
                    target_price = 0
                    price_match = re.search(r'(\d{1,3}(,\d{3})+)', full_title)
                    if price_match:
                        target_price = int(price_match.group(1).replace(',', ''))

                    # 💡 칸 이름에 맞춰 데이터 배달 (순서 절대 안 꼬임)
                    cur.execute('''
                        INSERT INTO reports (report_date, stock_code, stock_name, title, target_price, expert_name, source) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (report_date, stock_code, stock_name, full_title, target_price, expert, source))
                
                conn.commit()
                print(f"📄 네이버 {page}p 완료 (종목코드 확인: {stock_code})")
                time.sleep(0.5)
            except: break
        conn.close()
