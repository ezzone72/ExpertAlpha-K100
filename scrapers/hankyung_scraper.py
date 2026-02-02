import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import os
import sys

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def is_already_exists(self, title, date, expert_name):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # 제목, 날짜, 작성자가 모두 같으면 중복으로 간주
        cur.execute("SELECT id FROM reports WHERE title = ? AND report_date = ? AND expert_name = ?", (title, date, expert_name))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    def fetch_data(self, pages=5):
        print(f"📡 한경 컨센서스 수집 시작 (최대 {pages}페이지)...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        
        # 브라우저처럼 보이게 하는 필수 헤더
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://consensus.hankyung.com/'
        }
        
        for page in range(1, pages + 1):
            # skinType=stock (종목리포트) 페이징 URL
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock&pagenum=20&page={page}"
            
            try:
                res = requests.get(url, headers=headers, timeout=10)
                # 한경은 EUC-KR 대신 UTF-8을 쓰기도 하지만 한글 깨짐 방지를 위해 설정
                res.encoding = 'utf-8' 
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 데이터가 들어있는 테이블 행(tr) 찾기
                rows = soup.select('div.table_main table tbody tr')
                
                if not rows or len(rows) <= 1:
                    print(f"⚠️ {page}페이지에서 데이터를 찾을 수 없습니다. (구조 변경 의심)")
                    break

                duplicate_in_page = 0
                page_items = 0

                for row in rows:
                    cols = row.select('td')
                    # 한경 종목리포트 테이블은 보통 6~10개의 td를 가짐
                    if len(cols) < 5: continue
                    
                    page_items += 1
                    date = cols[0].text.strip() # 작성일 (YYYY-MM-DD)
                    title = cols[2].text.strip() # 제목
                    expert_name = cols[3].text.strip() # 작성자
                    source = cols[4].text.strip() # 증권사
                    
                    # 중복 체크
                    if self.is_already_exists(title, date, expert_name):
                        duplicate_in_page += 1
                        continue
                    
                    # DB 저장 (INSERT)
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date)
                        VALUES (?, ?, ?, ?)
                    ''', (title, expert_name, source, date))
                    new_count += 1
                
                conn.commit() # 페이지 단위 커밋
                print(f"📄 한경 {page}페이지 완료: {page_items - duplicate_in_page}개 신규 수집")
                
                # 모든 아이템이 중복이면 중단
                if page_items > 0 and duplicate_in_page == page_items:
                    print(f"🛑 중복 데이터 발견. 한경 수집 종료.")
                    break
                    
                time.sleep(0.5) # 차단 방지 지연
                
            except Exception as e:
                print(f"❌ 한경 {page}페이지 수집 중 에러: {e}")
                break

        conn.close()
        print(f"✅ 한경 총 {new_count}개 DB 저장 완료!")
