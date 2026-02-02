import sqlite3

def init_db(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 기존에 꼬인 테이블은 완전히 삭제하고 새로 만듭니다.
    cur.execute("DROP TABLE IF EXISTS reports") 
    
    # 데이터가 들어갈 칸(Column)을 명확하게 정의합니다.
    cur.execute('''
        CREATE TABLE reports (
            title TEXT,
            expert_name TEXT,
            source TEXT,
            report_date TEXT,
            stock_code TEXT,
            stock_name TEXT,
            target_price INTEGER DEFAULT 0,
            rating TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ DB 인프라 초기화 완료!")

if __name__ == "__main__":
    init_db()
