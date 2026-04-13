import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.runner import run_price_check
from core.repository import get_latest_run, build_run_side_summary


def render_missing_price_summary(missing_price_items: list[dict]) -> None:
    st.subheader('가격 없음')
    if missing_price_items:
        for item in missing_price_items:
            missing_text = ', '.join(item['missing_malls'])
            st.markdown(f"- **{item['item_name']}**: {missing_text}")
    else:
        st.caption('가격이 비어 있는 품목이 없습니다.')


st.set_page_config(page_title='채소팜 가격비교 관리자', layout='wide')
create_tables()
ensure_login()

st.markdown(
    """
    <style>
    div.stButton > button {
        font-size: 1.55rem;
        font-weight: 700;
        min-height: 3.8rem;
        padding: 0.5rem 2.2rem;
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
    latest_run = get_latest_run(session)
    if latest_run and latest_run.message_text:
        _, missing_price_items = build_run_side_summary(latest_run)
        left, right = st.columns([2.2, 1])
        with left:
            st.text_area('결과 복사', value=latest_run.message_text, height=420)
        with right:
            render_missing_price_summary(missing_price_items)
finally:
    session.close()
