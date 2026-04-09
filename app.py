import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.runner import run_price_check
from core.repository import get_latest_run

st.set_page_config(page_title='채소팜 가격비교 관리자', layout='wide')
create_tables()
ensure_login()

st.title('채소팜 가격비교 관리자')
st.caption('수동 실행은 웹에만 표시되고, 자동 실행만 텔레그램으로 발송됩니다.')

col1, col2 = st.columns([1, 2])
with col1:
    if st.button('지금 실행', use_container_width=True):
        with st.spinner('가격 비교 실행 중...'):
            try:
                result = run_price_check(trigger_type='manual')
                st.session_state['last_manual_result'] = result['message_text']
                st.success('수동 실행이 완료되었습니다.')
            except Exception as e:
                st.error(f'실행 중 오류: {e}')

with col2:
    st.info('웹 버튼으로 실행하면 텔레그램은 발송되지 않습니다.')

result_text = st.session_state.get('last_manual_result', '')
if result_text:
    st.subheader('방금 수동 실행한 결과')
    st.text(result_text)

session = get_session()
latest = get_latest_run(session)
if latest:
    st.subheader('최근 저장된 결과')
    st.write(f"구분: {latest.trigger_type} / 상태: {latest.status} / 시작: {latest.started_at}")
    st.text(latest.message_text)
session.close()
