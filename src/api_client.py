import requests

def get_quote(currency_pair: str = "XAU/INR"):
    url = 'https://www.mmtcpamp.com/api/getQuote'
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-IN,en;q=0.9',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.mmtcpamp.com',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    # The cookies have been removed to avoid exposing personal tracking IDs.
    
    payload = {
        "currencyPair": currency_pair,
        "type": "BUY"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

