from curl_cffi import requests
import re
import json

def get_safegold_price():
    url = "https://www.safegold.com/"
    # Use Chrome impersonation to avoid blocks
    r = requests.get(url, impersonate="chrome")
    
    # 1. Look for price in script tags (AngularJS often has a state object)
    # Search for "liveBuyPrice":1234.56 or similar
    match = re.search(r'\"liveBuyPrice\"\s*:\s*\"?([\d,]+\.?\d*)\"?', r.text)
    if match:
        return f"Found via liveBuyPrice: {match.group(1)}"
    
    # 2. Look for the price in the raw text with the currency symbol
    # SafeGold usually shows it as ₹ 16,836.66
    match = re.search(r'₹\s*([\d,]+\.\d{2})', r.text)
    if match:
        return f"Found via Rupee symbol: {match.group(1)}"
    
    # 3. Look for the rate in JSON-like structures
    # Often in ng-init or script tags
    match = re.search(r'rate\":\s*\"?(\d{4,5}\.\d{2})\"?', r.text)
    if match:
        return f"Found via rate keyword: {match.group(1)}"
    
    # 4. Search for the specific value 172933.23 we saw earlier
    if "172933.23" in r.text:
        return "Found 172933.23 in source!"

    return "Not found"

if __name__ == "__main__":
    print(get_safegold_price())
