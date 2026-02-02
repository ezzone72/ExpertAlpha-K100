import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=30):
        print(f"📡 [네이버 종목분석] {pages}페이지 수집 가동...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        success_count = 0
        for page in range(1, pages + 1):
            # 💡 노이즈 없는 '종목분석' 전용 섹션으로 타겟 고정
            url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
            try:
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('table.type_1 tr')
                
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # 종목명 (네이버는 첫 번째 칸에 종목명이 따로 나옵/니다)
                    stock_name = cols[0].text.strip()
                    title_a = cols[1].select_one('a')
                    title = title_a.text.strip()
                    
                    # 종목코드 (링크 주소에서 추출)
                    code_match = re.search(r'itemCode=(\d{6})', title_a['href'])
                    stock_code = code_match.group(1) if code_match else ""
                    
                    expert = cols[2].text.strip()
                    source = cols[3].text.strip()
                    date = cols[4].text.strip().replace('.', '-')
                    report_date = f"20{date}" if len(date) == 8 else date

                    if stock_code:
                        cur.execute('''
                            INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (report_date, stock_code, stock_name, 0, expert, source, title, "Naver"))
                        success_count += 1
                conn.commit()
                time.sleep(0.3)
            except: continue
        conn.close()
        print(f"✅ 네이버에서 {success_count}건 확보")
