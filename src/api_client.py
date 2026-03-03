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


async def get_quote(currency_pair: str = "XAU/INR", quote_type: str = "BUY") -> Dict[str, Any]:
    """
    Fetches the latest pricing quote asynchronously.
    Bypasses WAF protections by impersonating Chrome's TLS fingerprint.
    """
    payload = {
        "currencyPair": currency_pair,
        "type": quote_type
    }

    # impersonate="chrome110" spoofs Chrome's TLS fingerprint to bypass WAF blocks
    async with requests.AsyncSession(impersonate="chrome110") as session:
        response = await session.post(API_URL, headers=COMMON_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()

async def get_safegold_quote() -> Dict[str, Any]:
    """
    Fetches the latest SafeGold buy price via their internal API.
    Bypasses WAF by spoofing TLS and handling the TID/JWT handshake.
    """
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.safegold.com',
        'Referer': 'https://www.safegold.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    async with requests.AsyncSession(impersonate="chrome110") as session:
        # 1. Get Transaction ID (TID)
        tid_resp = await session.get("https://www.safegold.com/get-tid", headers=headers)
        tid_resp.raise_for_status()
        tid = tid_resp.json().get("tid")

        # 2. Fetch Buy Rate (Base64 for 'buy-rate')
        payload = {"csrf": tid, "upi": 0}
        buy_url = "https://www.safegold.com/YnV5LXJhdGU=" 
        
        response = await session.post(buy_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # 3. Decode JWT response
        jwt_token = response.text
        _, payload_b64, _ = jwt_token.split('.')
        payload_b64 += '=' * (-len(payload_b64) % 4)
        payload_data = json.loads(base64.b64decode(payload_b64))
        
        # 4. Extract data
        data_b64 = payload_data.get("data")
        if not data_b64:
            raise ValueError("No data found in SafeGold API response")
            
        data = json.loads(base64.b64decode(data_b64))
        return {
            "preTaxAmount": data.get("rate"),
            "source": "SafeGold"
        }
