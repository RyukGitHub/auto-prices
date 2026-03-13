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


# Removed _decode_sg_jwt as it is no longer needed.


async def get_sg_quote() -> Dict[str, Any]:
    """
    Fetches the latest SG buy and sell prices via their direct backend APIs.
    Bypasses WAF by spoofing TLS impersonation.
    """
    headers = {
        'accept': 'application/json',
        'origin': 'https://www.safegold.com',
        'referer': 'https://www.safegold.com/',
    }

    base_url = "https://website-backend.safegold.com/api/v1/metal/prices"
    buy_params = "?has_discount=0&discount_type=upi"

    async with requests.AsyncSession(impersonate="chrome110") as session:
        # 1. Gold Buy
        g_buy_resp = await session.get(
            f"{base_url}/buy/gold_9999{buy_params}", headers=headers
        )
        g_buy_resp.raise_for_status()
        g_buy = g_buy_resp.json().get("rate")

        # 2. Gold Sell
        g_sell_resp = await session.get(
            f"{base_url}/sell/gold_9999", headers=headers
        )
        g_sell_resp.raise_for_status()
        g_sell = g_sell_resp.json().get("rate")

        return {
            "buy": g_buy,
            "sell": g_sell,
            "source": "SafeGold"
        }
