import sqlite3, requests, re, time
from bs4 import BeautifulSoup

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # 💡 브라우저인 척 속이는 헤더 보강
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://consensus.hankyung.com/'
        }
        
        success_count = 0
        for page in range(1, pages + 1):
            url = f"http://consensus.hankyung.com/apps.analysis/analysis.list?&page={page}"
            try:
                res = requests.get(url, headers=headers, timeout=20)
                res.encoding = 'euc-kr' 
                
                # 💡 BeautifulSoup이 못 읽을 것에 대비해 정규식으로 직접 타격
                # <tr> 안의 <td>들을 덩어리째 낚아챕니다.
                html = res.text
                rows = re.findall(r'<tr.*?>(.*?)</tr>', html, re.DOTALL)
                
                for row_html in rows:
                    cols = re.findall(r'<td.*?>(.*?)</td>', row_html, re.DOTALL)
                    if len(cols) < 5: continue
                    
                    # 태그 제거하고 순수 텍스트만 추출
                    clean_cols = [re.sub(r'<.*?>', '', c).strip() for c in cols]
                    
                    report_date = clean_cols[0]
                    # 날짜 형식 체크 (예: 2026-02-02)
                    if not re.match(r'\d{4}-\d{2}-\d{2}', report_date): continue
                    
                    full_title = clean_cols[1]
                    target_price_raw = clean_cols[2].replace(',', '')
                    target_price = int(re.search(r'\d+', target_price_raw).group()) if re.search(r'\d+', target_price_raw) else 0
                    expert = clean_cols[3]
                    source = clean_cols[4]
                    
                    # 종목코드 추출 (000000)
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
                time.sleep(0.7) # 서버 차단 방지용 딜레이 살짝 증가
            except Exception as e:
                print(f"❌ {page}p 에러: {e}")
                continue
        conn.close()
