import streamlit as st
from core.config import APP_PASSWORD


def ensure_login() -> None:
    if st.session_state.get('authenticated'):
        return

    st.title('채소팜 가격비교 관리자 로그인')
    pw = st.text_input('비밀번호', type='password')
    if st.button('로그인'):
        if pw == APP_PASSWORD:
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error('비밀번호가 올바르지 않습니다.')
    st.stop()
