*** Settings ***
Library    Browser    timeout=60s    enable_playwright_debug=True
Library    BuiltIn

*** Variables ***
${URL}    https://www.safegold.com/

*** Test Cases ***
Fetch SafeGold Buy Price
    Given User Visits SafeGold Website
    When The Live Price Loads Completely
    Then We Get And Print The Buy Price In Logs

*** Keywords ***
User Visits SafeGold Website
    # Initialize a headless Chromium browser using robotframework-browser
    New Browser    chromium    headless=True    timeout=120s
    New Context    viewport={'width': 1920, 'height': 1080}    userAgent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36    extraHTTPHeaders={"Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"}
    # Use networkidle for full AngularJS/API binding completion
    New Page    ${URL}    wait_until=networkidle

The Live Price Loads Completely
    # Wait for the specific element class to become visible on the page
    # If it fails, robotframework-browser will auto-screenshot to the output dir
    Run Keyword And Ignore Error    Wait For Elements State    css=.livePrice_buy    visible    timeout=60s
    # Capture state for debugging regardless of success/fail during research phase
    Take Screenshot    selector=body
    # Price changes after initial load, so we wait for it to stabilize
    Sleep    5s

We Get And Print The Buy Price In Logs
    # Wait for the price container and specifically the price span
    Wait For Elements State    css=.livePrice_buy    visible    timeout=60s
    # Small sleep for angular binding to finalize
    Sleep    5s
    ${price}=    Get Text    css=.livePrice_buy h4 span
    Log    Live Buy Price is: ${price}    console=True
