import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import sys
import time

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import db_setup as database
except ImportError:
    import database

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def is_already_exists(self, title, date, expert_name):
        """DB를 조회하여 해당 리포트가 이미 존재하는지 확인"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        query = "SELECT id FROM reports WHERE title = ? AND report_date = ? AND expert_name = ?"
        cur.execute(query, (title, date, expert_name))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    def fetch_data(self, pages=10):
        print(f"📡 네이버 금융 리포트 수집 시작 (최대 {pages}페이지)...")
        new_count = 0
        
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            table = soup.select_one('table.type_1')
            rows = table.select('tr')
            
            duplicate_in_page = 0
            page_items = 0

            for row in rows:
                cols = row.select('td')
                if len(cols) < 5: continue
                
                page_items += 1
                title = cols[0].text.strip()
                expert_name = cols[1].text.strip()
                date = "20" + cols[4].text.strip().replace('.', '-') # 24.02.02 -> 2024-02-02
                
                # [지능형 체크] 이미 DB에 있는 리포트인가?
                if self.is_already_exists(title, date, expert_name):
                    duplicate_in_page += 1
                    continue
                
                # 데이터 저장 로직 (소장님 기존 코드의 저장 부분 호출)
                # self.save_to_db(title, expert_name, date, ...) 
                new_count += 1
            
            print(f"📄 {page}페이지 완료: {page_items - duplicate_in_page}개 신규 수집")
            
            # [핵심] 한 페이지의 모든 리포트가 이미 DB에 있다면, 과거 데이터가 다 채워진 것으로 보고 중단
            if page_items > 0 and duplicate_in_page == page_items:
                print(f"🛑 {page}페이지에서 중복 데이터 발견. 수집을 종료합니다.")
                break
                
            time.sleep(0.5) # 서버 부하 방지용 미세 지연

        print(f"✅ 총 {new_count}개의 새로운 리포트를 찾았습니다.")
