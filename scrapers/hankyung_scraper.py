import sqlite3, requests, time
from bs4 import BeautifulSoup

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=5):
        print("📡 [한경 컨센서스] 정밀 수집 가동...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for page in range(1, pages + 1):
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?&page={page}"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('div.table_style01 table tbody tr')
            
            for row in rows:
                cols = row.select('td')
                if len(cols) < 6: continue
                
                # 데이터 추출
                report_date = cols[0].text.strip()
                title = cols[1].text.strip()
                # 💡 목표가: '0'이거나 비어있으면 분석 가치 없음
                target_price_raw = cols[2].text.strip().replace(',', '')
                target_price = int(target_price_raw) if target_price_raw.isdigit() else 0
                
                expert_name = cols[3].text.strip()
                source_name = cols[4].text.strip()
                
                # 💡 종목명/코드 분리 (예: 삼성전자(005930))
                full_title = cols[1].select_one('a').get('title') or title
                import re
                code_match = re.search(r'\((\d{6})\)', full_title)
                stock_code = code_match.group(1) if code_match else ""
                stock_name = full_title.split('(')[0].strip() if stock_code else ""

                # 💡 종목코드와 목표가가 있는 '진짜' 리포트만 저장
                if stock_code and target_price > 0:
                    cur.execute('''
                        INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, "Hankyung"))
            
            conn.commit()
            print(f"📄 한경 {page}p 완료")
            time.sleep(1)
        conn.close()
