import FinanceDataReader as fdr
import sqlite3

def update_stock_list():
    # 1. 코스피 종목 리스트 가져오기
    print("📡 한국거래소(KRX)로부터 종목 리스트를 불러오는 중...")
    df_kospi = fdr.StockListing('KOSPI')

    # 2. 시가총액 순으로 상위 100개 추출 (KOSPI 100 대용)
    # 실제 KOSPI 100 지수 구성 종목과 유사하게 시총 상위 100개를 타겟팅합니다.
    top_100 = df_kospi.sort_values(by='MarCap', ascending=False).head(100)

    # 3. DB 연결
    conn = sqlite3.connect('expert_alpha.db')
    cur = conn.cursor()

    # 4. 데이터 삽입
    count = 0
    for _, row in top_100.iterrows():
        cur.execute('''
            INSERT OR REPLACE INTO stocks (stock_code, stock_name, sector)
            VALUES (?, ?, ?)
        ''', (row['Code'], row['Name'], row['Sector']))
        count += 1

    conn.commit()
    conn.close()
    print(f"✅ 총 {count}개 종목 정보를 'stocks' 테이블에 저장했습니다.")

if __name__ == "__main__":
    update_stock_list()
