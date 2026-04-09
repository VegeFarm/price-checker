import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import get_recent_runs_df, get_run_history, get_run_results_df

create_tables()
ensure_login()

st.title('실행 결과')
session = get_session()
try:
    history_df = get_recent_runs_df(session, limit=50)
    if history_df.empty:
        st.info('저장된 실행 이력이 없습니다.')
        st.stop()

    st.dataframe(history_df, use_container_width=True, hide_index=True)
    run_ids = history_df['run_id'].tolist()
    selected_run_id = st.selectbox('상세 보기 run_id', run_ids)
    run = get_run_history(session, int(selected_run_id))
    if run:
        st.subheader('결과 원문')
        st.text(run.message_text)
        st.download_button(
            '결과 txt 다운로드',
            data=run.message_text,
            file_name=f'가격비교_결과_{run.id}.txt',
            mime='text/plain',
        )
        detail_df = get_run_results_df(session, int(selected_run_id))
        st.subheader('결과 테이블')
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
finally:
    session.close()
