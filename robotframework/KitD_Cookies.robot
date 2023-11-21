*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    Dialogs
Library    OperatingSystem


*** Variables ***
${WSENDPOINT}  ws://192.168.85.2/playwright_0fd07572-30f4-491c-8655-da7a0a39bbb6/devtools/browser/80d28828-9e4e-4e4c-a898-abe11020711e
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
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}
        New Page  ${URL}
    END
    
    Record Click


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

