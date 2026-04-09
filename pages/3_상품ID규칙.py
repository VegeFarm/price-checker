import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import get_target_product_id_df, save_target_product_id_df

create_tables()
ensure_login()

st.title('상품 ID 규칙')
st.caption('상품명 x 쇼핑몰명별 target_product_id를 수정합니다.')
session = get_session()
try:
    df = get_target_product_id_df(session)
    edited_df = st.data_editor(df, use_container_width=True, num_rows='fixed', hide_index=True)
    if st.button('상품 ID 규칙 저장'):
        save_target_product_id_df(session, edited_df)
        st.success('상품 ID 규칙이 저장되었습니다.')
finally:
    session.close()
