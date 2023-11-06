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
Library    Browser
Library    OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py


*** Variables ***
${url}    https://djadelpeluqueria.es/

${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0
${COOKIES_DIR}   /tmp/djadelpeluqueria
${WORD_FILE}    ${OUTPUT_DIR}${/}example1.docx
${LOGO_SCREENSHOT}  ${OUTPUT_DIR}${/}logo.png
${escritorio}   Versión escritorio
${movil}        Versión móvil
${tableta}      Versión tableta

*** Test Cases ***
Get Title Screenshots and versions for URLs
    Create New Document    ${WORD_FILE}
    Open URL and Get Info    ${url}
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_PantallazosLogo.robot,PASS,,DOC:${WORD_FILE}|SCREENSHOT:${LOGO_SCREENSHOT}${\n}

*** Keywords *** 
Open URL and Get Info
    [Arguments]    ${url}
    New Persistent Context    userDataDir=${COOKIES_DIR}   browser=chromium  headless=False  url=${url}
    Wait For Elements State    xpath=//footer  visible
    Sleep  2
    Scroll TO Element  //footer
    Sleep  2
    Take Screenshot  filename=${LOGO_SCREENSHOT}
    Append Text And Picture To Document    ${WORD_FILE}  ${EMPTY}   ${EMPTY}    ${LOGO_SCREENSHOT}

    Close Browser
