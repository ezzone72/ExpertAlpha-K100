# 📈 ExpertAlpha-K100
> **"누가 진짜 전문가인가?"** - 증권사 리포트와 실제 주가 수익률의 상관관계 분석 프로젝트

## 🎯 프로젝트 목적
대한민국 증권사 애널리스트들의 리포트(비정형 데이터)를 분석하여 주가 등락 예측의 정확도를 측정합니다. 
단순한 상승/하락을 넘어, 코스피 지수 대비 초과 수익률(Alpha)을 계산함으로써 시장 상황 뒤에 숨은 전문가의 '진짜 실력'을 데이터로 검증합니다.

## 🛠 폴더 구조
- `/database`: SQLite 테이블 생성 및 전문가/주가 DB 관리
- `/scrapers`: 뉴스 데이터 및 리포트 요약본 크롤링 스크립트
- `/analysis`: LLM 기반 감성 분석 및 주가 상관관계(Backtesting) 로직
- `/data`: 주가 및 수집 데이터 보관 (CSV/DB)

## 🧠 핵심 분석 지표
1. **Alpha (순수 실력)**: `종목 수익률 - 코스피 지수 수익률` (시장 탓 방지 지표)
2. **Sentiment Score**: LLM을 활용한 리포트 텍스트의 긍정/부정 수치화
3. **Affiliation Tracking**: 전문가의 이직 이력을 추적하여 소속별/개인별 성적 산출
4. **Supply-Demand Check**: 기관/외국인 매매동향과 리포트 의견의 일치 여부

## 🏗 기술 스택
- **Language**: Python 3.x
- **Library**: BeautifulSoup4, FinanceDataReader, Pandas, SQLite3
- **AI**: LLM (Sentiment Analysis)
