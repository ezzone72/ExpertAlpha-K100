name: Daily Price Tracking

on:
  schedule:
    - cron: '0 9 * * *' # 매일 아침 9시(KST) 자동 실행
  workflow_dispatch: # 소장님이 원할 때 언제든 수동 실행

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: |
          pip install yfinance pandas

      - name: Run Tracking Engine
        run: python price_tracker.py

      - name: Commit and Push Changes
        run: |
          git config --global user.name "Jebanjang-AI"
          git config --global user.email "jebanjang@expertalpha.com"
          git add expert_score_board.csv
          # 변경사항이 있으면 커밋하고, 없으면 에러 없이 종료
          git commit -m "Update daily performance scores [ExpertAlpha-K100]" || exit 0
          git push
