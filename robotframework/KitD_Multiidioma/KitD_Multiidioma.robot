Navegar a la url de la página
Con la librería dialogs (https://robotframework.org/robotframework/latest/libraries/Dialogs.html), hacer un paso manual donde se selecciones el idioma manualmente dentro de la página.
Con las URLs de la página navegar a todas y hacer los pantallazos como en la tarea 5


*** Settings ***
Library    SeleniumLibrary
Library    word_helper.py
Library    Dialogs

*** Variables ***
${url1}    https://djadelpeluqueria.es/
${url2}    https://djadelpeluqueria.es/blog/
#${url3}    https://djadelpeluqueria.es/servicios/
#${url4}    https://djadelpeluqueria.es/contacto/
#${url5}    https://djadelpeluqueria.es/galeria-de-fotos/
#${url6}    https://djadelpeluqueria.es/acerca-de/


@{urls}    ${url1}  ${url2}
${WORD_FILE}    WebIdioma.docx


*** Test Cases ***
Get Title Screenshots and versions for URLs
    Create New Document    ${WORD_FILE}
    FOR    ${url}    IN    @{urls}
        Open URL and Get Info    ${url}
    END
    

*** Keywords *** 
Open URL and Get Info
    [Arguments]    ${url}
    Open Browser    ${url}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer 
    Click Element    xpath=//button[contains(text(), 'Aceptar')]

    Pause Execution    Cambia el idioma, luego pulsa OK para continuar.


    ${status}=    Run Keyword And Return Status    Get Title
    ${page_title}=    Run Keyword If    ${status}==True    Get Title    ELSE    Set Variable    ${EMPTY}

    Capture Page Screenshot    screenshot.png
    Append Text And Picture To Document    ${WORD_FILE}    ${page_title}    screenshot.png

    Close Browser

