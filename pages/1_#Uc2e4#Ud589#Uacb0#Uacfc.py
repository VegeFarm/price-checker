import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import (
    get_recent_runs_meta,
    get_run_history,
    build_run_side_summary,
)


def render_side_summary(large_gap_items: list[dict], missing_price_items: list[dict]) -> None:
    st.subheader('가격 차이 비교')
    if large_gap_items:
        for item in large_gap_items:
            st.markdown(
                f"- **{item['item_name']}**\n"
                f"  - 우리 {item['our_price']} | 평균 {item['avg_price']} | 최저 {item['min_price']}({item['min_mall']})\n"
                f"  - 평균 {item['avg_diff_amount']} ({item['avg_diff_ratio']}) | 최저 {item['min_diff_amount']} ({item['min_diff_ratio']})\n"
                f"  - {item['status_text']}"
            )
    else:
        st.caption('크게 벌어진 품목이 없습니다.')

    st.subheader('가격 없음')
    if missing_price_items:
        for item in missing_price_items:
            missing_text = ', '.join(item['missing_malls'])
            st.markdown(f"- **{item['item_name']}**: {missing_text}")
    else:
        st.caption('가격이 비어 있는 품목이 없습니다.')


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
            render_side_summary(large_gap_items, missing_price_items)
finally:
    session.close()
