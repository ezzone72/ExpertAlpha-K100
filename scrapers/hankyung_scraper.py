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
                res = requests.get(url, headers=headers, timeout=15)
                # 💡 한글 깨짐 방지
                res.encoding = 'euc-kr' 
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 💡 모든 테이블 행(tr)을 다 뒤집니다.
                rows = soup.find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 5: continue # 데이터가 있는 행만 골라냄
                    
                    # 작성일 (예: 2026-02-02)
                    report_date = cols[0].text.strip()
                    if not re.match(r'\d{4}-\d{2}-\d{2}', report_date): continue
                    
                    # 제목 및 종목정보
                    title_td = cols[1]
                    title_a = title_td.find('a')
                    if not title_a: continue
                    full_title = title_a.text.strip()
                    
                    # 목표가
                    tp_raw = cols[2].text.strip().replace(',', '')
                    target_price = int(re.sub(r'[^0-9]', '', tp_raw)) if any(d.isdigit() for d in tp_raw) else 0
                    
                    # 전문가 및 증권사
                    expert = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    # 종목코드 (제목에서 (000000) 형태 추출)
                    code_match = re.search(r'\((\d{6})\)', full_title)
                    if code_match:
                        stock_code = code_match.group(1)
                        stock_name = full_title.split('(')[0].strip()[-10:]
                        
                        cur.execute('''
                            INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (report_date, stock_code, stock_name, target_price, expert, source, full_title, "Hankyung"))
                        success_count += 1
                
                conn.commit()
                print(f"✔ {page}페이지 완료 (현재 누적 {success_count}건)")
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ {page}p 에러: {e}")
                continue
        conn.close()
