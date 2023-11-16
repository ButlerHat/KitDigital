*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 

*** Variables ***
# ${WSENDPOINT}    ws://localhost:9222/devtools/browser/0c3f4b1e-4b6a-4b6a-8c0c-8c0c8c0c8c0c


*** Test Cases ***
healthcheck
    TRY
        Connect To Browser Over Cdp    ${WSENDPOINT}
    EXCEPT
        Connect To Browser    ${WSENDPOINT}
    END