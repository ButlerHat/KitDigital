*** Settings ***
Library    OperatingSystem
Library    SeleniumLibrary

*** Variables ***
${url}=    https://djadelpeluqueria.es

*** Test Cases ***
Aceptar Cookies, Hacer Scroll y Capturar Pantallazo
    Open Browser    ${url}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer
    Click Element    xpath=//button[contains(text(), 'Aceptar')]
    Execute JavaScript    window.scrollTo(0, document.body.scrollHeight)
    Capture Page Screenshot
    Close Browser