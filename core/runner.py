from __future__ import annotations
from datetime import datetime
import time
from core.db import create_tables, get_session
from core.repository import load_runtime_config, save_run_result
from core.naver_client import create_session
from core.formatters import build_message_text
from core.telegram_sender import send_telegram_message


def apply_price_rule(display_name, mall_name, price_text, price_rules):
    if not price_text:
        return ""

    rules_by_item = price_rules.get(display_name, {})
    rule = rules_by_item.get(mall_name)
    if not rule:
        return price_text

    try:
        op, value = rule
        price = int(str(price_text).replace(',', '').strip())
        if op == 'mul':
            result = price * value
        elif op == 'add':
            result = price + value
        elif op == 'sub':
            result = price - value
        elif op == 'set':
            result = value
        elif op == 'rate':
            result = round(price * value)
        else:
            return price_text
        return f"{int(result):,}"
    except Exception:
        return price_text


def run_price_check(trigger_type: str = 'manual') -> dict:
    create_tables()
    started_at = datetime.now()
    session = get_session()
    rows = []
    message_text = ''
    try:
        target_malls, mall_display_names, search_keywords, target_product_ids, price_rules = load_runtime_config(session)
        api_session = create_session()
        results: dict[str, list[tuple[str, str]]] = {}

        for display_name, mall_keywords in search_keywords.items():
            mall_ids = target_product_ids.get(display_name, {})
            results[display_name] = []

            for mall in target_malls:
                if mall not in mall_keywords:
                    continue
                custom_keyword = mall_keywords[mall]
                target_id = mall_ids.get(mall, '')
                mall_display = mall_display_names.get(mall, mall)

                from core.naver_client import get_smart_api_price
                price = get_smart_api_price(
                    session=api_session,
                    display_name=display_name,
                    search_keyword=custom_keyword,
                    mall_name=mall,
                    target_id=target_id,
                )
                price = apply_price_rule(display_name, mall, price, price_rules)
                results[display_name].append((mall_display, price))
                rows.append({
                    'item_name': display_name,
                    'mall_name': mall,
                    'mall_display_name': mall_display,
                    'price_text': price,
                })
                time.sleep(0.2)

        message_text = build_message_text(results)
        finished_at = datetime.now()
        run_id = save_run_result(
            session=session,
            trigger_type=trigger_type,
            status='success',
            started_at=started_at,
            finished_at=finished_at,
            message_text=message_text,
            error_text='',
            rows=rows,
        )
        if trigger_type == 'cron':
            send_telegram_message(message_text)
        return {
            'status': 'success',
            'run_id': run_id,
            'message_text': message_text,
            'rows': rows,
        }
    except Exception as e:
        finished_at = datetime.now()
        run_id = save_run_result(
            session=session,
            trigger_type=trigger_type,
            status='fail',
            started_at=started_at,
            finished_at=finished_at,
            message_text=message_text,
            error_text=str(e),
            rows=rows,
        )
        raise
    finally:
        session.close()
