import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        print(f"📡 네이버 {pages}페이지 정밀 수집 가동...")
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
                    
                    # 💡 1순위: 제목에서 종목명과 코드 추출 (예: 삼성전자(005930))
                    stock_name, stock_code = "", ""
                    name_code_match = re.search(r'(.+?)\((\d{6})\)', full_title)
                    if name_code_match:
                        stock_name = name_code_match.group(1).strip()
                        stock_code = name_code_match.group(2).strip()
                    
                    # 💡 2순위: 제목엔 없지만 링크 주소에 코드가 숨어있는 경우 (네이버 특성)
                    if not stock_code and title_a and 'href' in title_a.attrs:
                        code_match = re.search(r'itemCode=(\d{6})', title_a['href'])
                        if code_match:
                            stock_code = code_match.group(1)

                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    
                    # 날짜 (24.12.15 -> 2024-12-15)
                    raw_date = cols[4].text.strip()
                    report_date = f"20{raw_date.replace('.', '-')}" if len(raw_date) == 8 else raw_date.replace('.', '-')

                    # 목표가 추출
                    target_price = 0
                    price_match = re.search(r'(\d{1,3}(,\d{3})+)', full_title)
                    if price_match:
                        target_price = int(price_match.group(1).replace(',', ''))

                    # 💡 DB 저장 (정해진 칸에 쏙쏙)
                    cur.execute('''
                        INSERT INTO reports (report_date, stock_code, stock_name, title, target_price, expert_name, source) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (report_date, stock_code, stock_name, full_title, target_price, expert, source))
                
                conn.commit()
                # 잘 되고 있는지 로그로 확인!
                if stock_code:
                    print(f"📄 {page}p 완료: 최근 수집 종목 [{stock_name}({stock_code})]")
                else:
                    print(f"📄 {page}p 완료: (시장/섹터 리포트 위주)")
                
                time.sleep(0.3)
            except Exception as e:
                print(f"❌ {page}p 에러: {e}")
                break
        conn.close()
