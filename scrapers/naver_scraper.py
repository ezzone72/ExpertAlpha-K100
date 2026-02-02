import sqlite3, requests, re, time

class NaverScraper:
    def __init__(self, db_path='expert_alpha_v4.db'):
        self.db_path = db_path

    def fetch_data(self, pages=20):
        print(f"📡 [긴급 소스변경] 컴퍼니가이드 데이터 수집 중...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 💡 네이버 대신 좀 더 관대한 데이터 서버를 공략
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        success_count = 0
        # 컴퍼니가이드의 최신 리포트 요약 경로
        url = "http://comp.fnguide.com/SVO2/ASP/SVD_Report_Summary.asp"
        
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            
            # 정규식으로 종목명, 코드, 목표가, 증권사를 통째로 낚아챕니다.
            # 💡 패턴: 종목명(코드), 제목, 목표가, 투자의견, 증권사, 날짜 순
            items = re.findall(r'<tr.*?>.*?<span.*?>(.*?)</span>.*?<span.*?>(.*?)</span>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>', res.text, re.DOTALL)
            
            for item in items:
                # 데이터 매핑 (사이트 구조에 따라 인덱스 조정)
                raw_name_code = item[0] # 예: 삼성전자(005930)
                title = item[1]
                target_price = int(item[2].replace(',', '')) if item[2].replace(',', '').isdigit() else 0
                source = item[4]
                report_date = item[6]
                
                code_match = re.search(r'\((\d{6})\)', raw_name_code)
                if code_match:
                    stock_code = code_match.group(1)
                    stock_name = raw_name_code.split('(')[0]
                    
                    cur.execute('''
                        INSERT INTO reports (report_date, stock_code, stock_name, target_price, expert_name, source_name, title, report_source) 
                        VALUES (?, ?, ?, ?, '전문가', ?, ?, 'FnGuide')
                    ''', (report_date, stock_code, stock_name, target_price, source, title))
                    success_count += 1
            
            conn.commit()
            print(f"✅ FnGuide에서 {success_count}건 긴급 확보 성공!")
            
        except Exception as e:
            print(f"❌ 접속 실패: {e}")
            
        conn.close()
