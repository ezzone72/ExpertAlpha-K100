import sqlite3

def init_db():
    conn = sqlite3.connect('expert_alpha_v3.db')
    cur = conn.cursor()
    
    # 1. 종목 정보 테이블 (추가됨!)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT UNIQUE,
        stock_code TEXT
    )
    """)
    
    # 임시 데이터: 테스트를 위해 종목 몇 개 미리 넣어두기
    # (나중에 fetch_stock_list.py가 이 테이블을 채우게 됩니다)
    sample_stocks = [('삼성전자', '005930'), ('SK하이닉스', '000660'), ('현대차', '005380')]
    cur.executemany("INSERT OR IGNORE INTO stocks (stock_name, stock_code) VALUES (?, ?)", sample_stocks)

    # 2. 전문가/기자 통합 출처 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        source_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        provider TEXT,
        organization TEXT,
        UNIQUE(name, provider, organization)
    )
    """)
    
    # 3. 발언/리포트 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS statements (
        statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER,
        stock_name TEXT,
        issue_date DATE,
        title TEXT,
        FOREIGN KEY(source_id) REFERENCES sources(source_id)
    )
    """)
    
    # 4. 주가 및 지수 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT,
        date DATE,
        close_price INTEGER,
        kospi_index REAL,
        UNIQUE(stock_code, date)
    )
    """)

    # 5. 일일 성적 히스토리
    cur.execute("""
    CREATE TABLE IF NOT EXISTS performance_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER,
        record_date DATE,
        avg_alpha REAL,
        total_count INTEGER,
        FOREIGN KEY(source_id) REFERENCES sources(source_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ database.py: stocks 테이블 포함 인프라 재구축 완료!")

if __name__ == "__main__":
    init_db()
