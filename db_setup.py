import sqlite3

def init_db(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print(f"🛠️ DB 테이블 최적화 및 생성 중... ({db_path})")

    # 1. 리포트 저장 테이블 (reports)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            expert_name TEXT,
            source TEXT,
            report_date TEXT,
            stock_code TEXT,
            stock_name TEXT,
            target_price INTEGER,
            rating TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 주가 및 종목 정보 테이블 (stocks)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            stock_code TEXT PRIMARY KEY,
            stock_name TEXT,
            current_price INTEGER,
            last_updated TEXT
        )
    ''')

    # 3. 전문가 성적 기록 테이블 (history)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expert_name TEXT,
            avg_return REAL,
            hit_rate REAL,
            record_date TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 모든 테이블 인프라 구축 완료 (reports, stocks, history)")

if __name__ == "__main__":
    init_db()
