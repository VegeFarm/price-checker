import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import get_recent_runs_df, get_recent_runs_meta, get_run_history

create_tables()
ensure_login()

st.title('실행 결과')
session = get_session()
try:
    history_df = get_recent_runs_df(session, limit=3)
    runs_meta = get_recent_runs_meta(session, limit=3)
    if history_df.empty or not runs_meta:
        st.info('저장된 실행 이력이 없습니다.')
        st.stop()

    option_map = {
        f"{meta['run_id']} | {meta['구분']} | {meta['시작']}": meta['actual_run_id']
        for meta in runs_meta
    }
    selected_label = st.selectbox('저장된 실행 결과', list(option_map.keys()))
    run = get_run_history(session, option_map[selected_label])
    if run:
        keyword = st.text_input('결과 검색')
        display_text = run.message_text
        if keyword:
            filtered_lines = [line for line in run.message_text.splitlines() if keyword.lower() in line.lower()]
            display_text = '\n'.join(filtered_lines)

        left, right = st.columns(2)
        with left:
            st.subheader('결과')
            st.text(display_text)
        with right:
            st.text_area('결과 복사', value=display_text, height=400)
finally:
    session.close()
