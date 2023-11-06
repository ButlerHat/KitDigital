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
Library    Collections
Library    Dialogs
Library    OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py

*** Variables ***
${url1}    https://djadelpeluqueria.es/
${url2}    https://djadelpeluqueria.es/blog/
${url3}    https://djadelpeluqueria.es/servicios/
${url4}    https://djadelpeluqueria.es/contacto/
${url5}    https://djadelpeluqueria.es/galeria-de-fotos/
${url6}    https://djadelpeluqueria.es/acerca-de/

${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0
${COOKIES_DIR}   /tmp/djadelpeluqueria
${WORD_FILE_TEMPLATE}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/Plantilla.docx
${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/PlantillaPelu.docx


*** Test Cases ***
Get Title Screenshots and versions for URLs
    # Get Urls
    @{urls}=    Create List
    ${variables}=  Get variables
    FOR  ${i}  IN RANGE  1  30
        ${STATUS}  ${MSG}  Run Keyword And Ignore Error   Should be true      "\${url${i}}" in $variables
        IF  "${STATUS}"=="PASS"
            Append To List    ${urls}    ${url${i}}
            Log  ${url${i}} appended to list  console=${true}
            CONTINUE
        ELSE
            BREAK
        END
    END

    # Copy template
    # Copy File    ${WORD_FILE_TEMPLATE}  ${WORD_FILE}

    # Create New Document    ${WORD_FILE}
    ${urls_incomplete}  Check If Identifier Exists    ${WORD_FILE}    {PANTALLAZOS_MULTI-IDIOMA}

    IF  ${urls_incomplete}
        FOR    ${url}    IN    @{urls}
            Open URL and Get Info    ${url}
        END
        Remove Identifier    ${WORD_FILE}    {PANTALLAZOS_MULTI-IDIOMA}
        Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_PantallazosUrls.robot,PASS,,Se han anadido los pantallazos de los dispositivos${\n}
    ELSE
        Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_PantallazosUrls.robot,PASS,,Ya se habia ejecutado${\n}
        Skip  Ya se habia ejecutado
    END

*** Keywords *** 
Open URL and Get Info
    [Arguments]    ${url}
    New Persistent Context    userDataDir=${COOKIES_DIR}   browser=chromium  headless=False  url=${url}
    Wait For Elements State    xpath=//footer  visible

    Dialogs.Pause Execution  Obteniendo pantallazo de ${url}.${\n} Por favor, cambia la página de idioma.${\n}${\n}Pulse OK cuando esté listo.
    ${status}=    Run Keyword And Return Status    Get Title
    ${page_title}=    Run Keyword If    ${status}==True    Get Title    ELSE    Set Variable    ${EMPTY}

    Sleep  1
    Take Screenshot  filename=${OUTPUT_DIR}${/}screenshot_${page_title}.png
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_MULTI-IDIOMA}   ${page_title}    ${OUTPUT_DIR}${/}screenshot_${page_title}.png

    Close Browser

