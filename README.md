# 채소팜 가격비교 관리자

수동 실행은 웹에서만 결과를 보여주고, 자동 실행(Render Cron Job)만 텔레그램으로 발송합니다.
결과 텍스트 형식은 기존 스크립트의 `*상품명 / 쇼핑몰명 - 가격` 형식을 그대로 유지합니다.

## 1) 로컬 실행

```bash
pip install -r requirements.txt
copy .env.example .env
python scripts/init_db.py
python scripts/seed_initial_data.py
streamlit run app.py
```

자동 실행 테스트:

```bash
python cron_entry.py
```

## 2) Render Web Service

- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## 3) Render Cron Job

- Build Command: `pip install -r requirements.txt`
- Start Command: `python cron_entry.py`
- 예시 스케줄(한국시간 08:30): `30 23 * * *`  # UTC 기준

## 4) 꼭 넣어야 하는 환경변수

- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- DATABASE_URL
- APP_PASSWORD

## 5) 최초 1회 세팅

로컬에서 `scripts/seed_initial_data.py`를 한 번 실행해도 되고,
Render Shell이 가능하면 그 안에서 아래를 1회 실행해도 됩니다.

```bash
python scripts/init_db.py
python scripts/seed_initial_data.py
```
