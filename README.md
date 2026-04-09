# 채소팜 가격비교 관리자

수동 실행은 웹에서만 결과를 보여주고, 자동 실행(Render Cron Job)만 텔레그램으로 발송합니다.
결과 텍스트 형식은 기존 스크립트의 `*상품명 / 쇼핑몰명 - 가격` 형식을 그대로 유지합니다.

## 주요 변경점

- 관리자 비밀번호 제거
- 실행 결과 최대 3개만 저장
- 실행 결과 페이지에서 원문 전체 복사 가능
- 실행 결과 페이지의 결과 테이블 제거
- 검색규칙에서 삭제한 상품은 저장 후 다시 열어도 보이지 않도록 수정
- 표시 시간은 한국시간으로 보이도록 수정

## Render Web Service

- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Render Cron Job

- Build Command: `pip install -r requirements.txt`
- Start Command: `python cron_entry.py`
- 예시 스케줄(한국시간 08:00): `0 23 * * *`  # UTC 기준

## 꼭 넣어야 하는 환경변수

- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- DATABASE_URL

## 최초 1회 세팅

Render Shell 또는 one-off 환경에서 아래를 1회 실행합니다.

```bash
python scripts/init_db.py
python scripts/seed_initial_data.py
```
