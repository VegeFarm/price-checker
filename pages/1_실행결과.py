import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import (
    get_recent_runs_meta,
    get_run_history,
    build_run_side_summary,
)

create_tables()
ensure_login()

st.title('실행 결과')
session = get_session()
try:
    runs_meta = get_recent_runs_meta(session, limit=3)
    if not runs_meta:
        st.info('저장된 실행 이력이 없습니다.')
        st.stop()

    option_map = {
        f"{meta['run_id']} | {meta['구분']} | {meta['시작']}": meta['actual_run_id']
        for meta in runs_meta
    }
    selected_label = st.selectbox('저장된 실행 결과', list(option_map.keys()))
    run = get_run_history(session, option_map[selected_label])
    if run:
        large_gap_items, missing_price_items = build_run_side_summary(run)
        left, right = st.columns([2.2, 1])
        with left:
            st.subheader('결과')
            st.text(run.message_text)
        with right:
            st.subheader('가격 차이 큰 품목')
            if large_gap_items:
                for item in large_gap_items:
                    st.markdown(
                        f"- **{item['item_name']}**\n  - 최저: {item['min_mall']} {item['min_price']}\n  - 최고: {item['max_mall']} {item['max_price']}\n  - 차이: {item['diff_price']}"
                    )
            else:
                st.caption('큰 가격 차이 품목이 없습니다.')

            st.subheader('가격 없음')
            if missing_price_items:
                for item in missing_price_items:
                    missing_text = ', '.join(item['missing_malls'])
                    st.markdown(f"- **{item['item_name']}**: {missing_text}")
            else:
                st.caption('가격이 비어 있는 품목이 없습니다.')
finally:
    session.close()
