import sqlite3

def init_db(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS reports") # 기존 꼬인 테이블 삭제
    cur.execute('''
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            expert_name TEXT,
            source TEXT,
            report_date TEXT,
            stock_code TEXT,
            stock_name TEXT,
            target_price INTEGER DEFAULT 0,
            rating TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ DB 테이블 정밀 리셋 완료!")
