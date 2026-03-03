from curl_cffi import requests
import re
import os

def check_safegold():
    url = "https://www.safegold.com/"
    r = requests.get(url, impersonate="chrome")
    print(f"Status: {r.status_code}")
    
    # Save the HTML for inspection
    with open("safegold_debug.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    # Try multiple patterns
    # 1. Look for something that looks like the price ₹ 16,836.66
    matches = re.findall(r'(\d{1,2}[\d,]{2,}\.\d{2})', r.text)
    print(f"Digit patterns found: {matches}")
    
    # 2. Look for the specific class in the source (might be empty but let's check)
    if ".livePrice_buy" in r.text:
        print("Found class .livePrice_buy in source!")
    
    # 3. Look for any JSON-like structures that might contain rates
    if '"rate"' in r.text or '"gold_rate"' in r.text:
        print("Found rate keyword in source!")

if __name__ == "__main__":
    check_safegold()
