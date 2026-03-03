*** Settings ***
Documentation     Example test to verify project structure
Library           Process

*** Variables ***
${API_ENDPOINT}   http://127.0.0.1:8000/trigger

*** Test Cases ***
Verify Project Structure is Setup
    [Documentation]    Simple test to verify robot is working
    Log    Robot Framework BDD is configured correctly!
    Should Be Equal    1    1
