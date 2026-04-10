import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.runner import run_price_check
from core.repository import get_recent_runs_df, get_latest_run

st.set_page_config(page_title='채소팜 가격비교 관리자', layout='wide')
create_tables()
ensure_login()

st.markdown(
    """
    <style>
    div.stButton > button {
        font-size: 1.4rem;
        font-weight: 700;
        min-height: 3.4rem;
        padding: 0.4rem 1.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('채소팜 가격비교 관리자')

if st.button('지금 실행', type='primary'):
    with st.spinner('가격 비교 실행 중...'):
        try:
            run_price_check(trigger_type='manual')
            st.rerun()
        except Exception as e:
            st.error(f'실행 중 오류: {e}')

session = get_session()
try:
    recent_df = get_recent_runs_df(session, limit=3)
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

    latest_run = get_latest_run(session)
    if latest_run and latest_run.message_text:
        st.text_area('결과 복사', value=latest_run.message_text, height=360)
finally:
    session.close()
