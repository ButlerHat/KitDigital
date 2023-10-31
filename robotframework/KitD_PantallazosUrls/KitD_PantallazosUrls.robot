# https://youtu.be/KkGvbPF79X8?t=300

# Hacer un robot que dada una lista de urls:
# En *** Variables *** declarar una lista @{urls} <url1> <url2> <url3>
# Obtener el H1 y pantallazo por cada url (bucle FOR)
# Guardar en un Word

https://youtu.be/KkGvbPF79X8?t=327
# Para la página principal hacer pantallazos en todas las versiones. Para ello, se puede usar la keyword Set Viewport Size y Take Screenshot
# Obtener pantallazo versión móvil (viewport: 375x667)
# Obtener pantallazo versión iPad Mini (viewport: 768x1024)
# Obtener pantallazo versión navegador (viewport: 1280x800)
# Guardar en el word



*** Settings ***
Library    SeleniumLibrary
Library    word_helper.py

*** Variables ***
${url1}    https://djadelpeluqueria.es/
${url2}    https://djadelpeluqueria.es/blog/
#${url3}    https://djadelpeluqueria.es/servicios/
#${url4}    https://djadelpeluqueria.es/contacto/
#${url5}    https://djadelpeluqueria.es/galeria-de-fotos/
#${url6}    https://djadelpeluqueria.es/acerca-de/


@{urls}    ${url1}  ${url2}
${WORD_FILE}    example.docx
${escritorio}   Versión escritorio
${movil}        Versión móvil
${tableta}      Versión tableta

*** Test Cases ***
Get Title Screenshots and versions for URLs
    Create New Document    ${WORD_FILE}
    FOR    ${url}    IN    @{urls}
        Open URL and Get Info    ${url}
    END
    Take Different Version Screenshots    ${urls[0]}

*** Keywords *** 
Open URL and Get Info
    [Arguments]    ${url}
    Open Browser    ${url}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer 
    Click Element    xpath=//button[contains(text(), 'Aceptar')]
    ${status}=    Run Keyword And Return Status    Get Title
    ${page_title}=    Run Keyword If    ${status}==True    Get Title    ELSE    Set Variable    ${EMPTY}

    Capture Page Screenshot    screenshot.png
    Append Text And Picture To Document    ${WORD_FILE}    ${page_title}    screenshot.png

    Close Browser

Take Different Version Screenshots
    [Arguments]    ${url}
    Open Browser    ${url}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer
    Click Element    xpath=//button[contains(text(), 'Aceptar')]
    Set Window Size    375      667
    Capture Page Screenshot   mobile_screenshot.png
    Set Window Size    768    1024
    Capture Page Screenshot   ipad_screenshot.png
    Set Window Size    1280    800
    Capture Page Screenshot   desktop_screenshot.png
    Close Browser
    Append Text And Picture To Document    ${WORD_FILE}   ${movil}       mobile_screenshot.png
    Append Text And Picture To Document    ${WORD_FILE}   ${tableta}     ipad_screenshot.png
    Append Text And Picture To Document    ${WORD_FILE}   ${escritorio}  desktop_screenshot.png
