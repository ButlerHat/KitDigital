*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    Dialogs
Library    OperatingSystem


*** Variables ***
# ${WSENDPOINT}  ws://192.168.85.2/playwright_645a6215-bef9-4789-bd67-deb2098ddfc5/ws
${URL}    https://djadelpeluqueria.es/
${COOKIES_DIR}    ${OUTPUT_DIR}${/}cookies
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0

*** Test Cases ***

Aceptar Cookies
    [Tags]  1
    # Check if is a WS endpoint
    ${variables}=  Get variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para el kit digital se usara el navegador completo
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}
            New Page  ${URL}
        END
    ELSE
        New Browser  chromium  headless=${False}
    END
    
    Record Click


StoreCookies
    [Tags]  2
    Connect To Browser Over Cdp    ${WSENDPOINT}
    ${storage_state}  Save Storage State
    Close Page
    Copy File    ${storage_state}  ${COOKIES_DIR}${/}cookies.json
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_Cookies.robot,PASS,,Se han aceptado las cookies${\n}

