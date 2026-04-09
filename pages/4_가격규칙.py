import streamlit as st
import pandas as pd
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import get_price_rule_df, save_price_rule_df, get_items, get_malls

create_tables()
ensure_login()

st.title('가격 규칙')
st.caption('연산은 mul(곱하기), add(더하기), sub, set, rate 중 하나를 사용합니다.')
session = get_session()
try:
    df = get_price_rule_df(session)
    items = [x.display_name for x in get_items(session)]
    malls = [x.mall_name for x in get_malls(session)]
    if df.empty:
        df = pd.DataFrame([{'상품명': '', '쇼핑몰명': '', '연산': '', '값': ''}])
    df['값'] = df['값'].astype(str)
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows='dynamic',
        hide_index=True,
        column_config={
            '상품명': st.column_config.SelectboxColumn(options=items),
            '쇼핑몰명': st.column_config.SelectboxColumn(options=malls),
            '연산': st.column_config.SelectboxColumn(options=['mul', 'add', 'sub', 'set', 'rate']),
            '값': st.column_config.TextColumn(),
        },
    )
    if st.button('가격 규칙 저장'):
        save_price_rule_df(session, edited_df)
        st.success('가격 규칙이 저장되었습니다.')
finally:
    session.close()
