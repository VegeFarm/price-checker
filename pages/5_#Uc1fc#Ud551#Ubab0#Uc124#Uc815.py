import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import get_mall_settings_df, save_mall_settings_df

create_tables()
ensure_login()

st.title('쇼핑몰 설정')
st.caption('쇼핑몰 표시명, 사용여부, 정렬순서를 수정합니다.')
session = get_session()
try:
    df = get_mall_settings_df(session)
    edited_df = st.data_editor(df, use_container_width=True, num_rows='dynamic', hide_index=True)
    if st.button('쇼핑몰 설정 저장'):
        save_mall_settings_df(session, edited_df)
        st.success('쇼핑몰 설정이 저장되었습니다.')
finally:
    session.close()
