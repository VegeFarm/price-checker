import re
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET


class MissingNaverCredentialsError(RuntimeError):
    pass


def create_session() -> requests.Session:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        raise MissingNaverCredentialsError('NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수를 먼저 넣어주세요.')

    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    })
    return session


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<.*?>", "", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_match(text):
    text = clean_html(text)
    text = text.lower()
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"[^0-9a-z가-힣]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_title_match(search_keyword, product_title):
    keyword_norm = normalize_for_match(search_keyword)
    title_norm = normalize_for_match(product_title)

    keyword_tokens = [t for t in keyword_norm.split() if t]
    if not keyword_tokens:
        return False

    matched = sum(1 for token in keyword_tokens if token in title_norm)

    if len(keyword_tokens) == 1:
        return matched >= 1
    return matched / len(keyword_tokens) >= 0.7


def get_smart_api_price(session, display_name, search_keyword, mall_name, target_id=""):
    url = "https://openapi.naver.com/v1/search/shop.json"

    for start in range(1, 1001, 100):
        params = {
            "query": f"{search_keyword} {mall_name}",
            "display": 100,
            "start": start,
            "sort": "sim",
        }

        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("items", [])

            if not results and start == 1:
                return ""

            candidates = []
            for product in results:
                found_mall = clean_html(product.get("mallName", ""))
                found_title = clean_html(product.get("title", ""))
                found_price = product.get("lprice", "")
                found_product_id = str(product.get("productId", ""))
                found_mall_product_id = str(product.get("mallProductId", ""))

                if target_id and (found_product_id == str(target_id) or found_mall_product_id == str(target_id)):
                    try:
                        return f"{int(found_price):,}"
                    except Exception:
                        return str(found_price)

                if found_mall == mall_name and is_title_match(search_keyword, found_title):
                    candidates.append((found_title, found_price, found_product_id))

            if candidates:
                _, best_price, _ = candidates[0]
                try:
                    return f"{int(best_price):,}"
                except Exception:
                    return str(best_price)

            time.sleep(0.15)
        except requests.exceptions.Timeout:
            return ""
        except requests.exceptions.RequestException:
            return ""
        except Exception:
            return ""

    return ""
