import sqlite3

def init_db(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS reports") 
    cur.execute('''
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,
            stock_code TEXT,
            stock_name TEXT,
            title TEXT,
            target_price INTEGER,
            expert_name TEXT,
            source TEXT,
            rating TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ [시스템] DB 구조를 완벽하게 재설정했습니다.")
