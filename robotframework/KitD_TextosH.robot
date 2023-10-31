*** Settings ***
Library    Browser
Library    OperatingSystem

*** Variables ***
${url}=    https://djadelpeluqueria.es

*** Test Cases ***
Obtener Textos de Encabezados
    Open Browser    ${url}    browser=chromium
    wait until network is idle
    ${h1_elements}=    Get Elements    xpath=//h1
    ${h2_elements}=    Get Elements    xpath=//h2
    ${h3_elements}=    Get Elements    xpath=//h3
    Create File    textos.txt    ${url}\n
    FOR    ${element}    IN    @{h1_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    textos.txt    H1 - ${text}\n
    END
    FOR    ${element}    IN    @{h2_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    textos.txt    H2 - ${text}\n
    END
    FOR    ${element}    IN    @{h3_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    textos.txt    H3 - ${text}\n
    END
    Close Browser

