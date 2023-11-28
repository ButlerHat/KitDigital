*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    Dialogs
Library    OperatingSystem


*** Variables ***
${WSENDPOINT}  ws://192.168.85.2/playwright_bd1e34b9-959f-4d08-b9c5-2d4ff36ecaee/devtools/browser/2f23ee9b-17c5-4f91-bb24-2cfbb64d0dc5
${URL}    https://djadelpeluqueria.es/
${COOKIES_DIR}    ${OUTPUT_DIR}${/}cookies
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0

*** Test Cases ***

Aceptar Cookies
    [Tags]  1
    # Check if is a WS endpoint
    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        Connect To Browser Over Cdp    ${WSENDPOINT}
        Go To  ${URL}
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}
        New Page  ${URL}
    END
    
    # Record Click


StoreCookies
    [Tags]  2
    TRY
        Connect To Browser Over Cdp    ${WSENDPOINT}
    EXCEPT
        Connect To Browser    ${WSENDPOINT}
    END
    ${storage_state}  Save Storage State
    Close Page
    Copy File    ${storage_state}  ${COOKIES_DIR}${/}cookies.json
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_Cookies.robot,PASS,,Se han aceptado las cookies${\n}

