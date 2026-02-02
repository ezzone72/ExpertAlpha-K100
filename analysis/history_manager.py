import sqlite3
import datetime

class HistoryManager:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def record_daily_scores(self):
        """매일의 전문가 성적을 스냅샷으로 기록합니다."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        print(f"📈 {today} 기준 전문가 성적 히스토리 기록 중...")

        # 쿼리: 전문가별 현재까지의 누적 알파 수익률 계산 및 저장
        query = """
        INSERT INTO performance_history (source_id, record_date, avg_alpha, total_count)
        SELECT 
            s.source_id,
            ?,
            AVG((CAST((p_future.close_price - p_issue.close_price) AS FLOAT) / p_issue.close_price) - 
                (CAST((p_future.kospi_index - p_issue.kospi_index) AS FLOAT) / p_issue.kospi_index)) * 100,
            COUNT(st.statement_id)
        FROM sources s
        JOIN statements st ON s.source_id = st.source_id
        JOIN stocks stk ON st.stock_name = stk.stock_name
        JOIN stock_prices p_issue ON stk.stock_code = p_issue.stock_code AND p_issue.date = st.issue_date
        JOIN stock_prices p_future ON stk.stock_code = p_future.stock_code 
            AND p_future.date = (
                SELECT MIN(date) FROM stock_prices 
                WHERE stock_code = stk.stock_code AND date >= date(st.issue_date, '+6 days')
            )
        GROUP BY s.source_id
        """
        
        try:
            cur.execute(query, (today,))
            conn.commit()
            print("✅ 일일 성적 기록 완료!")
        except Exception as e:
            print(f"❌ 기록 실패: {e}")
        finally:
            conn.close()
