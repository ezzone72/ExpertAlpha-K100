import sqlite3

def init_db(db_path='expert_alpha_v4.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS reports")
    cur.execute('''
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT,      -- 리포트 작성일 (YYYY-MM-DD)
            stock_code TEXT,       -- 종목코드 (6자리)
            stock_name TEXT,       -- 종목명
            target_price INTEGER,  -- 목표주가 (숫자)
            expert_name TEXT,      -- 애널리스트 실명
            source_name TEXT,      -- 소속 증권사
            title TEXT,            -- 리포트 제목
            report_source TEXT,    -- 데이터 출처 (Hankyung/Naver)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ [설계] 법적 근거 확보가 가능한 DB 구조로 셋업 완료.")
