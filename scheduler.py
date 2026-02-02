import schedule
import time
import subprocess
import datetime

def job():
    print(f"⏰ [작업 시작] {datetime.datetime.now()} - 데이터 수집 및 분석 가동")
    
    max_retries = 3
    attempt = 0
    success = False
    
    while attempt < max_retries and not success:
        try:
            # 1. 주가 업데이트 및 수집 실행 (main.py 호출)
            # 30분 동안 세밀하게 긁기 위해 pages 수를 넉넉히 잡은 상태로 가정
            result = subprocess.run(['python3', 'main.py', '--update-prices'], check=True)
            
            if result.returncode == 0:
                print("✅ 작업 성공!")
                success = True
        except Exception as e:
            attempt += 1
            print(f"❌ 작업 실패 (시도 {attempt}/{max_retries}): {e}")
            time.sleep(60) # 1분 후 재시도

# 한국 시간 23:30분에 실행 설정
schedule.every().day.at("23:30").do(job)

print("📡 스케줄러가 대기 중입니다... (매일 밤 23:30 실행)")

while True:
    schedule.run_pending()
    time.sleep(1)
