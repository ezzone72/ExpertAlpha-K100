import sqlite3

def init_db(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS reports")
    # 💡 순서를 [날짜, 코드, 이름, 제목, 가격, 전문가, 증권사]로 강제 고정
    cur.execute('''
        CREATE TABLE reports (
            report_date TEXT,
            stock_code TEXT,
            stock_name TEXT,
            title TEXT,
            target_price INTEGER,
            expert_name TEXT,
            source TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')
    conn.commit()
    conn.close()
