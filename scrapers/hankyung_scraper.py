import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import sys

# 파일명 충돌 방지를 위한 경로 처리
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import db_setup as database
except ImportError:
    import database

class HankyungScraper:
    def __init__(self, db_path='expert_alpha_v3.db'):
        self.db_path = db_path

    def fetch_data(self, pages=5):
        print(f"📡 한경 컨센서스 리포트 수집 시작 ({pages} 페이지)...")
        # 수집 로직... (이후 기존 소장님 코드의 수집 로직 유지)
        print("✅ 한경 리포트 수집 완료")
