import sqlite3

def create_db():
    # 데이터베이스 연결 (파일이 없으면 자동 생성)
    conn = sqlite3.connect('expert_alpha.db')
    cur = conn.cursor()

    # 1. 전문가 기본 정보 테이블 (experts)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS experts (
            expert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            total_career_years INTEGER
        )
    ''')

    # 2. 소속 변동 이력 테이블 (affiliation_history)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS affiliation_history (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_id INTEGER,
            organization TEXT NOT NULL,
            position TEXT,
            start_date DATE,
            end_date DATE,
            stay_duration INTEGER,
            FOREIGN KEY (expert_id) REFERENCES experts (expert_id)
        )
    ''')

    # 3. 발언 및 리포트 기록 테이블 (statements)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS statements (
            statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_id INTEGER,
            affiliation_seq INTEGER,
            issue_date DATE NOT NULL,
            stock_name TEXT NOT NULL,
            target_price INTEGER,
            sentiment_score REAL,
            headline TEXT,
            source_url TEXT,
            FOREIGN KEY (expert_id) REFERENCES experts (expert_id),
            FOREIGN KEY (affiliation_seq) REFERENCES affiliation_history (seq)
        )
    ''')

    # 4. 주가 및 지수 데이터 테이블 (stock_prices)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            date DATE NOT NULL,
            open_price INTEGER,
            close_price INTEGER,
            high_price INTEGER,
            low_price INTEGER,
            volume INTEGER,
            kospi_index REAL,
            FOREIGN KEY (stock_code) REFERENCES stocks (stock_code)
        )
    ''')

    # 5. 종목 정보 테이블 (stocks) - 코스피 100 리스트용
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            stock_code TEXT PRIMARY KEY,
            stock_name TEXT NOT NULL,
            sector TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ ExpertAlpha-K100 데이터베이스 및 테이블 생성 완료!")

if __name__ == "__main__":
    create_db()
