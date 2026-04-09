import streamlit as st
from core.auth import ensure_login
from core.db import create_tables
from core.runner import run_price_check

st.set_page_config(page_title='채소팜 가격비교 관리자', layout='wide')
create_tables()
ensure_login()

st.title('채소팜 가격비교 관리자')

if st.button('지금 실행', use_container_width=True):
    with st.spinner('가격 비교 실행 중...'):
        try:
            result = run_price_check(trigger_type='manual')
            st.session_state['last_manual_result'] = result['message_text']
            st.success('수동 실행이 완료되었습니다.')
        except Exception as e:
            st.error(f'실행 중 오류: {e}')

result_text = st.session_state.get('last_manual_result', '')
if result_text:
    st.subheader('실행 결과')
    st.text(result_text)
