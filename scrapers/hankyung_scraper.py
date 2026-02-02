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
        print(f"📡 한경 컨센서스 모바일 경로 침투 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 브라우저 헤더를 모바일 기기(아이폰)처럼 위장
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'http://m.consensus.hankyung.com/'
        }
        
        new_count = 0
        for page in range(1, pages + 1):
            # 💡 모바일용 리스트 주소입니다. (주소 구조가 다릅니다)
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock&pagenum=20&page={page}"
            
            try:
                res = requests.get(url, headers=headers, timeout=15)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 모바일/PC 통합 구조에서 tr 요소를 다 가져옵니다.
                rows = soup.select('tr')
                
                page_added = 0
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # 날짜 형식 체크 (YYYY-MM-DD)
                    date_raw = cols[0].text.strip()
                    if len(date_raw) != 10 or "-" not in date_raw: continue
                    
                    title = cols[2].text.strip()
                    expert = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    if self.is_already_exists(title, date_raw, expert):
                        continue
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date)
                        VALUES (?, ?, ?, ?)
                    ''', (title, expert, source, date_raw))
                    page_added += 1
                    new_count += 1
                
                conn.commit()
                # 💡 한경도 첫 제목을 찍어서 페이지가 넘어가는지 확인하겠습니다.
                sample_title = rows[1].select('td')[2].text.strip()[:10] if len(rows) > 1 else "No Data"
                print(f"📄 한경 {page}p 완료: {page_added}개 추가 (첫제목: {sample_title}...)")
                
                if page_added == 0 and page > 10: # 10페이지 연속 0개면 이미 다 채워진 것
                    print("🏁 한경 과거 데이터 수집 완료 구간 도달.")
                    break
                    
                time.sleep(0.7)
                
            except Exception as e:
                print(f"❌ 한경 {page}p 에러: {e}")
                break

        conn.close()
        print(f"✅ 한경 총 {new_count}개 DB 저장 완료!")
