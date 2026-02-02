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

class HankyungScraper:
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

    def fetch_data(self, pages=5):
        print(f"📡 한경 컨센서스 리포트 수집 시작 (최대 {pages}페이지)...")
        new_count = 0
        
        # 한경 컨센서스 기본 URL (종목 리포트 기준)
        base_url = "http://consensus.hankyung.com/apps.analysis/analysis.list?skinType=stock"
        
        for page in range(1, pages + 1):
            url = f"{base_url}&pagenum=20&page={page}"
            # 한경은 User-Agent가 없으면 거부할 수 있어 추가합니다.
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            table = soup.select_one('div.table_main table')
            if not table: break
            
            rows = table.select('tbody tr')
            duplicate_in_page = 0
            page_items = 0

            for row in rows:
                cols = row.select('td')
                if len(cols) < 6: continue
                
                page_items += 1
                date = cols[0].text.strip() # 한경은 보통 YYYY-MM-DD 형식
                title = cols[2].text.strip()
                expert_name = cols[3].text.strip() # 작성자(애널리스트)
                
                # [지능형 체크] 이미 DB에 있는 리포트인가?
                if self.is_already_exists(title, date, expert_name):
                    duplicate_in_page += 1
                    continue
                
                # 여기에 소장님의 기존 저장 로직(INSERT 문 등)이 들어갑니다.
                # 예: self.save_to_db(date, title, expert_name, ...)
                new_count += 1
            
            print(f"📄 한경 {page}페이지 완료: {page_items - duplicate_in_page}개 신규 수집")
            
            # [핵심] 해당 페이지가 전부 중복이면 과거 데이터 수집 완료로 간주하고 중단
            if page_items > 0 and duplicate_in_page == page_items:
                print(f"🛑 {page}페이지에서 중복 데이터 발견. 한경 수집을 종료합니다.")
                break
                
            time.sleep(0.5)

        print(f"✅ 한경 총 {new_count}개의 새로운 리포트를 찾았습니다.")
