import sqlite3

def setup_database(db_path='expert_alpha_v3.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 기존 테이블 삭제 (깔끔하게 새로 시작)
    cur.execute("DROP TABLE IF EXISTS reports")
    
    # 테이블 생성 (분석에 필요한 모든 컬럼 배치)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reports (
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
    print("✅ DB 테이블 구조 재설정 완료!")

if __name__ == "__main__":
    setup_database()
