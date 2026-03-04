"""Async HTTP client for fetching gold and silver price."""
import base64
import json
from typing import Dict, Any

from curl_cffi import requests

API_URL = 'https://www.mmtcpamp.com/api/getQuote'
COMMON_HEADERS = {
    'accept': 'application/json',
    'accept-language': 'en-IN,en;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://www.mmtcpamp.com',
    'priority': 'u=1, i',
    'sec-ch-ua': (
        '"Not:A-Brand";v="99", '
        '"Google Chrome";v="145", '
        '"Chromium";v="145"'
    ),
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/145.0.0.0 Safari/537.36'
    )
}


async def get_quote(
    currency_pair: str = "XAU/INR",
    quote_type: str = "BUY"
) -> Dict[str, Any]:
    """
    Fetches the latest pricing quote asynchronously.
    Bypasses WAF protections by impersonating Chrome's TLS fingerprint.
    """
    payload = {
        "currencyPair": currency_pair,
        "type": quote_type
    }

    # impersonate="chrome110" spoofs Chrome's TLS fingerprint
    # to bypass WAF blocks
    async with requests.AsyncSession(impersonate="chrome110") as session:
        response = await session.post(
            API_URL, headers=COMMON_HEADERS, json=payload
        )
        response.raise_for_status()
        return response.json()


def _decode_sg_jwt(jwt_token: str) -> Dict[str, Any]:
    """Decodes SafeGold's nested Base64 JWT response."""
    _, payload_b64, _ = jwt_token.split('.')
    payload_b64 += '=' * (-len(payload_b64) % 4)
    payload_data = json.loads(base64.b64decode(payload_b64))

    data_b64 = payload_data.get("data")
    if not data_b64:
        raise ValueError("No data found in SG API response")

    return json.loads(base64.b64decode(data_b64))


async def get_sg_quote() -> Dict[str, Any]:
    """
    Fetches the latest SG buy and sell prices via their internal APIs.
    Bypasses WAF by spoofing TLS and handling the TID/JWT handshake.
    """
    headers_www = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.safegold.com',
        'Referer': 'https://www.safegold.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    async with requests.AsyncSession(impersonate="chrome110") as session:
        # 1. Get Transaction ID (TID)
        tid_url = "https://www.safegold.com/get-tid"
        tid_resp = await session.get(tid_url, headers=headers_www)
        tid_resp.raise_for_status()
        tid = tid_resp.json().get("tid")

        # 2. Fetch Buy Rate (POST to www.safegold.com)
        payload_buy = {"csrf": tid, "upi": 0}
        buy_url = "https://www.safegold.com/YnV5LXJhdGU="
        buy_resp = await session.post(
            buy_url, headers=headers_www, json=payload_buy
        )
        buy_resp.raise_for_status()

        # Decode Buy JWT using helper
        buy_data = _decode_sg_jwt(buy_resp.text)

        # 3. Fetch Sell Rate (GET from website-backend using TID as Bearer)
        sell_url = (
            'https://website-backend.safegold.com/'
            'api/v1/metal/prices/sell/gold_9999'
        )
        headers_sell = {
            'accept': 'application/json',
            'authorization': f'Bearer {tid}',
            'origin': 'https://app.safegold.com',
            'referer': 'https://app.safegold.com/',
            'x-sg-captcha-action': 'gold_price'
        }
        sell_resp = await session.get(sell_url, headers=headers_sell)
        sell_resp.raise_for_status()
        sell_data = sell_resp.json()

        return {
            "buy": buy_data.get("rate"),
            "sell": sell_data.get("rate"),
            "source": "SafeGold"
        }
