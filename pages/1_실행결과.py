import html
import re
import streamlit as st
from core.auth import ensure_login
from core.db import create_tables, get_session
from core.repository import (
    get_recent_runs_meta,
    get_run_history,
    get_previous_run,
    build_run_side_summary,
    build_price_map_by_item_mall,
)


PLUS_COLOR = '#66C6F2'
MINUS_COLOR = '#F48FB1'


def render_large_gap_summary(large_gap_items: list[dict]) -> None:
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


def _price_to_int(price_text: str) -> int | None:
    text = str(price_text or '').replace(',', '').replace('원', '').strip()
    if not text:
        return None
    try:
        return int(float(text))
    except Exception:
        return None


def _parse_item_name(line: str) -> str | None:
    if not line.startswith('*'):
        return None
    return line[1:].strip()


def _parse_price_line(line: str) -> tuple[str, str, int | None] | None:
    match = re.match(r'^\s*([^*\-][^-]*?)\s*-\s*(.*)$', line.strip())
    if not match:
        return None
    mall_name = match.group(1).strip()
    price_text = match.group(2).strip()
    return line, mall_name, _price_to_int(price_text)


def _format_delta_html(delta: int) -> str:
    if delta == 0:
        return ''
    color = PLUS_COLOR if delta > 0 else MINUS_COLOR
    sign = '+' if delta > 0 else '-'
    return f' <span style="color: {color}; font-weight: 700;">({sign}{abs(delta):,})</span>'


def build_message_html_with_previous_diff(message_text: str, previous_price_map: dict[str, dict[str, int]]) -> str:
    current_item = ''
    rendered_lines: list[str] = []

    for raw_line in message_text.splitlines():
        line = raw_line.rstrip()
        item_name = _parse_item_name(line)
        if item_name is not None:
            current_item = item_name
            rendered_lines.append(f'<strong>{html.escape(line)}</strong>')
            continue

        parsed = _parse_price_line(line)
        if parsed and current_item:
            original_line, mall_name, current_price = parsed
            previous_price = previous_price_map.get(current_item, {}).get(mall_name)
            base_html = html.escape(original_line)
            if current_price is not None and previous_price is not None:
                delta = current_price - previous_price
                rendered_lines.append(base_html + _format_delta_html(delta))
            else:
                rendered_lines.append(base_html)
            continue

        if line:
            rendered_lines.append(html.escape(line))
        else:
            rendered_lines.append('&nbsp;')

    return '<div style="line-height: 1.8; white-space: pre-wrap;">' + '<br>'.join(rendered_lines) + '</div>'


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
        large_gap_items, _ = build_run_side_summary(run)
        previous_run = get_previous_run(session, run.id)
        previous_price_map = build_price_map_by_item_mall(previous_run)

        left_pad, center_col, right_pad = st.columns([1.65, 1.45, 0.9])
        with center_col:
            render_large_gap_summary(large_gap_items)

        st.subheader('결과')
        st.markdown(build_message_html_with_previous_diff(run.message_text, previous_price_map), unsafe_allow_html=True)
finally:
    session.close()
