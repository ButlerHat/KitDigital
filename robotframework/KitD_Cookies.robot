*** Settings ***
Library    Browser 
Library    Dialogs
Library    OperatingSystem


*** Variables ***
${URL}    https://djadelpeluqueria.es/
${COOKIES_DIR}    ${OUTPUT_DIR}${/}cookies
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv


*** Test Cases ***

Aceptar Cookies
    New Persistent Context  userDataDir=${COOKIES_DIR}  browser=chromium  headless=${False}  url=${URL}
    Dialogs.Pause Execution    message=Por favor, acepta las cookies
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_Cookies.robot,PASS,,Se han aceptado las cookies${\n}

