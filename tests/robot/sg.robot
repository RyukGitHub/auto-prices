*** Settings ***
Library    Browser

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
    New Browser    chromium    headless=True    timeout=60s
    New Context
    New Page    ${URL}    wait_until=domcontentloaded

The Live Price Loads Completely
    # Wait for the specific element class to become visible on the page
    Wait For Elements State    css=.livePrice_buy    visible    timeout=30s
    # Price changes after initial load, so we wait for it to stabilize
    Sleep    3s

We Get And Print The Buy Price In Logs
    # Extract the text and print it explicitly to the console log
    ${price}=    Get Text    css=.livePrice_buy
    Log    Live Buy Price is: ${price}    console=True

