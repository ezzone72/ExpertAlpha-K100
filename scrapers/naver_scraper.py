import sqlite3, requests, time

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=50):
        print(f"📡 [네이버 API] {pages}페이지 뒷문 타격 중...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 💡 브라우저 헤더를 더 정교하게 세팅
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://finance.naver.com/research/company_list.naver'
        }
        
        success_count = 0
        for page in range(1, pages + 1):
            # 💡 HTML이 아니라 데이터를 직접 쏴주는 주소입니다.
            url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
            
            try:
                res = requests.get(url, headers=headers, timeout=15)
                # 💡 이번엔 '단순 텍스트'로 긁어서 종목코드 6자리와 이름을 강제로 찾아냅니다.
                import re
                # <a href="company_read.naver?nid=65432&page=1&itemCode=005930" class="stock_item">삼성전자</a>
                matches = re.findall(r'itemCode=(\d{6})".*?>(.*?)</a>.*?<a href="company_read.*?>(.*?)</a>', res.text, re.DOTALL)
                
                for match in matches:
                    stock_code = match[0]
                    stock_name = match[1].strip()
                    title = match[2].strip()
                    
                    # 💡 데이터가 있다면 저장
                    if stock_code:
                        cur.execute('''
                            INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                            VALUES (date('now'), ?, ?, 0, '전문가', '증권사', ?, 'Naver_API')
                        ''', (stock_code, stock_name, title))
                        success_count += 1
                
                conn.commit()
                print(f"✔ API {page}p 완료 (누적 {success_count}건)")
                time.sleep(0.5)
            except:
                continue
                
        conn.close()
        print(f"🏁 최종 {success_count}건 확보.")
