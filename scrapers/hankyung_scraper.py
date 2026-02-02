import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import datetime

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def is_already_exists(self, title, date, expert_name):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM reports WHERE title = ? AND report_date = ? AND expert_name = ?", (title, date, expert_name))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    def fetch_data(self, pages=5):
        print(f"📡 한경 컨센서스 강제 수집 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 1년 전부터 오늘까지로 날짜 범위 강제 설정
        edate = datetime.datetime.now().strftime('%Y-%m-%d')
        sdate = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        
        new_count = 0
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for page in range(1, pages + 1):
            # 검색 조건(sdate, edate)을 URL에 명시적으로 추가
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock&sdate={sdate}&edate={edate}&pagenum=20&page={page}"
            
            try:
                res = requests.get(url, headers=headers, timeout=15)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.select('div.table_main table tbody tr')
                
                if not rows:
                    print(f"⚠️ {page}페이지에 행(row)이 없습니다.")
                    break

                page_new_count = 0
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5 or "데이터가 없습니다" in row.text: continue
                    
                    date = cols[0].text.strip()
                    title = cols[2].text.strip()
                    expert_name = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    if self.is_already_exists(title, date, expert_name):
                        continue
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date)
                        VALUES (?, ?, ?, ?)
                    ''', (title, expert_name, source, date))
                    page_new_count += 1
                    new_count += 1
                
                conn.commit()
                print(f"📄 한경 {page}페이지 완료: {page_new_count}개 신규 추가")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                break

        conn.close()
        print(f"✅ 한경 총 {new_count}개 DB 저장 완료!")
