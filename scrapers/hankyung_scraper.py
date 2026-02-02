import sqlite3, requests, time, datetime
from bs4 import BeautifulSoup

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        print(f"📡 한경 컨센서스 [실전 분석형] 수집 시작...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'}
        
        for page in range(1, pages + 1):
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock&pagenum=20&page={page}"
            try:
                res = requests.get(url, headers=headers, timeout=15)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('tr')
                
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 8: continue # 한경은 컬럼이 많음
                    
                    date = cols[0].text.strip()
                    if len(date) != 10: continue
                    
                    # 💡 종목명과 제목이 섞여있을 경우 처리
                    title = cols[2].text.strip()
                    expert = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    # 💡 투자의견 및 목표가 (한경의 핵심 데이터)
                    rating = cols[5].text.strip()
                    target_price = 0
                    try:
                        target_price = int(cols[6].text.strip().replace(',', ''))
                    except: target_price = 0
                    
                    cur.execute("SELECT id FROM reports WHERE title=? AND report_date=?", (title, date))
                    if cur.fetchone(): continue
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date, target_price, rating) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, expert, source, date, target_price, rating))
                    new_count += 1
                
                conn.commit()
                print(f"📄 한경 {page}p: {new_count}개 누적 (Target: {target_price})")
                time.sleep(0.5)
            except: break
        conn.close()
