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
        print(f"📡 한경 컨센서스 특공대 수집 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 날짜 설정
        edate = datetime.datetime.now().strftime('%Y-%m-%d')
        sdate = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 세션 생성 (쿠키 유지를 위함)
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock'
        }
        
        # 1. 먼저 메인 페이지에 접속해서 세션/쿠키를 구워옵니다.
        session.get("http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock", headers=headers)
        
        new_count = 0
        for page in range(1, pages + 1):
            # 2. 세션을 유지한 채로 실제 리스트 요청
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?sdate={sdate}&edate={edate}&skinType=stock&pagenum=20&page={page}"
            
            try:
                res = session.get(url, headers=headers, timeout=20)
                res.encoding = 'utf-8' # 한경은 종종 EUC-KR이 섞이기도 함
                
                if "검색결과가 없습니다" in res.text:
                    print(f"📍 {page}페이지: 검색 결과 끝.")
                    break
                
                soup = BeautifulSoup(res.text, 'html.parser')
                # 한경의 실제 데이터 테이블 id인 'list_contents'를 직접 공략합니다.
                rows = soup.select('tr') 
                
                page_new_count = 0
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # '날짜'가 YYYY-MM-DD 형식이 아니면 건너뜁니다 (헤더 방지)
                    date_raw = cols[0].text.strip()
                    if len(date_raw) != 10 or "-" not in date_raw: continue
                    
                    title = cols[2].text.strip()
                    expert_name = cols[3].text.strip()
                    source = cols[4].text.strip()
                    
                    if self.is_already_exists(title, date_raw, expert_name):
                        continue
                    
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date)
                        VALUES (?, ?, ?, ?)
                    ''', (title, expert_name, source, date_raw))
                    page_new_count += 1
                    new_count += 1
                
                conn.commit()
                print(f"📄 한경 {page}페이지 완료: {page_new_count}개 수집")
                
                # 만약 한 페이지에 데이터가 하나도 없으면 루프 탈출
                if page_new_count == 0 and page > 1:
                    # 중복 때문이 아니라 진짜 데이터가 없는 건지 확인
                    if "데이터가 없습니다" in res.text: break
                
                time.sleep(1.0) # 한경은 좀 더 천천히 (차단 방지)
                
            except Exception as e:
                print(f"❌ 에러: {e}")
                break

        conn.close()
        print(f"✅ 한경 총 {new_count}개 수집 완료!")
