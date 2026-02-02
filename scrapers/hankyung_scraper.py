import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        success_count = 0
        for page in range(1, pages + 1):
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?&page={page}"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('div.table_style01 table tbody tr')
                
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # 1. 날짜 및 제목
                    report_date = cols[0].text.strip()
                    title_a = cols[1].select_one('a')
                    full_title = title_a.get('title') or title_a.text.strip()
                    
                    # 2. 목표가 (문자 섞여있어도 숫자만 추출)
                    tp_raw = cols[2].text.strip().replace(',', '')
                    tp_match = re.search(r'\d+', tp_raw)
                    target_price = int(tp_match.group()) if tp_match else 0
                    
                    # 3. 전문가 및 증권사
                    expert = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    # 4. 종목코드 정밀 추출
                    code_match = re.search(r'\((\d{6})\)', full_title)
                    if code_match:
                        stock_code = code_match.group(1)
                        stock_name = full_title.split('(')[0].strip()[-15:] # 종목명만 잘라내기
                        
                        cur.execute('''
                            INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (report_date, stock_code, stock_name, target_price, expert, source, full_title, "Hankyung"))
                        success_count += 1
                conn.commit()
                print(f"✔ {page}페이지 완료 (누적 {success_count}건)")
                time.sleep(0.5)
            except: continue
        conn.close()
