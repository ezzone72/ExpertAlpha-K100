import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import re

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=10):
        print(f"📡 네이버 금융 리포트 [정밀 분석형] 수집 시작...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        new_count = 0
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/research/invest_list.naver?&page={page}"
            try:
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                # 데이터가 있는 테이블 행(tr)
                rows = soup.select('table.type_1 tr')
                
                for row in rows:
                    cols = row.select('td')
                    if len(cols) < 5: continue
                    
                    # 1. 종목명 및 종목코드 추출 (제목 옆의 링크에서 추출)
                    title_cell = cols[0]
                    title = title_cell.text.strip()
                    
                    # 상세 페이지 링크나 종목 연결 링크가 있는지 확인
                    link_tag = title_cell.select_one('a')
                    stock_code = ""
                    if link_tag and 'href' in link_tag.attrs:
                        # href에서 itemCode=000000 형태를 추출
                        code_match = re.search(r'itemCode=(\d{6})', link_tag['href'])
                        if code_match:
                            stock_code = code_match.group(1)

                    # 2. 전문가, 증권사, 날짜
                    expert = cols[1].text.strip()
                    source = cols[2].text.strip()
                    raw_date = cols[4].text.strip()
                    date = "20" + raw_date.replace('.', '-') if len(raw_date) == 8 else raw_date.replace('.', '-')

                    # 3. 목표주가 (한경은 표에 있지만 네이버는 제목에 섞여 있는 경우가 많음)
                    # 우선은 기본 컬럼 위주로 수집하되, 종목코드를 확보하는 것이 급선무입니다.
                    
                    # 중복 체크
                    cur.execute("SELECT id FROM reports WHERE title=? AND report_date=? AND expert_name=?", (title, date, expert))
                    if cur.fetchone(): continue
                    
                    # 4. DB 저장 (종목코드 포함)
                    cur.execute('''
                        INSERT INTO reports (title, expert_name, source, report_date, stock_code) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (title, expert, source, date, stock_code))
                    new_count += 1
                
                conn.commit()
                print(f"📄 네이버 {page}p 완료: {new_count}개 누적 저장 (최근코드: {stock_code})")
                time.sleep(0.3)
            except Exception as e:
                print(f"❌ 에러: {e}")
                break
        
        conn.close()
