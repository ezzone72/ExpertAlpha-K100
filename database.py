import sqlite3

def init_db():
    conn = sqlite3.connect('expert_alpha_v3.db')
    cur = conn.cursor()
    
    # 1. 전문가/기자 통합 출처 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        source_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,          -- 'ANALYST' 또는 'REPORTER'
        provider TEXT,      -- 'NAVER', 'HANKYUNG', 'DAUM'
        organization TEXT,
        UNIQUE(name, provider, organization)
    )
    """)
    
    # 2. 발언/리포트 테이블
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
    
    # 3. 주가 및 지수 테이블 (이전 DB에서 복사하거나 새로 수집)
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

    # 4. 일일 성적 히스토리 (성적 변화 추적용 핵심 테이블!)
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
    print("✅ database.py: v3.0 통합 DB 인프라 구축 완료!")

if __name__ == "__main__":
    init_db()
