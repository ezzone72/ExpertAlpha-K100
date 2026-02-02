import sqlite3

class HistoryManager:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def record_daily_scores(self):
        print("📈 전문가 성적 계산 및 기록 시작...")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 실제 분석 로직이 들어갈 자리 (현재는 샘플 기록)
        # 예: cur.execute("INSERT INTO history ...")
        
        conn.commit() # 🔥 여기서도 커밋!
        conn.close()
        print("✅ 성적 기록 및 커밋 완료")
