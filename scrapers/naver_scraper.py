import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=30):
        print(f"📡 [네이버 종목분석] {pages}페이지 긴급 수집...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        success_count = 0
        for page in range(1, pages + 1):
            # 💡 여기가 '진짜' 종목 리포트만 모여있는 곳입니다.
            url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
            try:
                res = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 테이블 행 추출
                rows = soup.select('table.type_1 tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 5: continue
                    
                    # 1. 종목명 (첫 번째 칸)
                    stock_name = cols[0].text.strip()
                    if not stock_name: continue
                    
                    # 2. 제목 및 종목코드 (두 번째 칸)
                    title_td = cols[1]
                    title_a = title_td.find('a')
                    if not title_a: continue
                    title = title_a.text.strip()
                    
                    # 💡 링크에서 6자리 코드 추출
                    code_match = re.search(r'itemCode=(\d{6})', title_a['href'])
                    stock_code = code_match.group(1) if code_match else ""
                    
                    # 3. 전문가, 증권사, 날짜
                    expert = cols[2].text.strip()
                    source = cols[3].text.strip()
                    raw_date = cols[4].text.strip().replace('.', '-')
                    report_date = f"20{raw_date}" if len(raw_date) == 8 else raw_date

                    if stock_code:
                        cur.execute('''
                            INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (report_date, stock_code, stock_name, 0, expert, source, title, "Naver"))
                        success_count += 1
                
                conn.commit()
                print(f"✔ 네이버 {page}p 완료 (누적 {success_count}건)")
                time.sleep(0.3)
            except Exception as e:
                print(f"❌ 에러: {e}")
                continue
        conn.close()
