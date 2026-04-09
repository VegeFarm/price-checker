import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.runner import run_price_check
from core.repository import get_recent_runs_df

st.set_page_config(page_title='채소팜 가격비교 관리자', layout='wide')
create_tables()
ensure_login()

st.title('채소팜 가격비교 관리자')

if st.button('지금 실행'):
    with st.spinner('가격 비교 실행 중...'):
        try:
            run_price_check(trigger_type='manual')
            st.success('수동 실행이 완료되었습니다.')
        except Exception as e:
            st.error(f'실행 중 오류: {e}')

session = get_session()
try:
    latest_df = get_recent_runs_df(session, limit=1)
    if not latest_df.empty:
        st.dataframe(latest_df, use_container_width=True, hide_index=True)
finally:
    session.close()
