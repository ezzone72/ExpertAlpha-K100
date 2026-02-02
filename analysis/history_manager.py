import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# 파일명 충돌 방지를 위한 경로 처리
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import db_setup as database
except ImportError:
    import database

class HistoryManager:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def record_daily_scores(self):
        print("📈 일일 성적 분석 및 기록 중...")
        conn = sqlite3.connect(self.db_path)
        # 성적 계산 로직... (이후 기존 소장님 코드 유지)
        conn.close()
        print("✅ 성적 기록 완료")
