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
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    Collections
Library    OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py

*** Variables ***
# ${url1}    https://djadelpeluqueria.es/
# ${url2}    https://djadelpeluqueria.es/blog/
# ${url3}    https://djadelpeluqueria.es/servicios/
# ${url4}    https://djadelpeluqueria.es/contacto/
# ${url5}    https://djadelpeluqueria.es/galeria-de-fotos/
# ${url6}    https://djadelpeluqueria.es/acerca-de/

# ${WSENDPOINT}
# ${UTILS_ENDPOINT}
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0
# ${COOKIES_DIR}   /tmp/djadelpeluqueria
${WORD_FILE_TEMPLATE}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/Plantilla.docx
${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/PlantillaPelu.docx
${escritorio}   Versión escritorio (1280x800)
${movil}        Versión móvil, iPhone (375x667)
${tableta}      Versión tableta, iPad Mini (768x1024)


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

    FOR    ${url}    IN    @{urls}
        Open URL and Get Info    ${url}
    END

    Take Different Version Screenshots    ${urls[0]}
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_PantallazosUrls.robot,PASS,,Se han anadido los pantallazos de los dispositivos${\n}


*** Keywords *** 
Open URL and Get Info
    [Arguments]    ${url}
    
    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Add All Cookies From State  ${COOKIES_DIR}${/}cookies.json
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}  storageState=${COOKIES_DIR}${/}cookies.json
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}  storageState=${COOKIES_DIR}${/}cookies.json
        New Page  ${URL}
    END

    Sleep  2
    # Click    xpath=//button[contains(text(), 'Aceptar')]
    ${status}=    Run Keyword And Return Status    Get Title
    ${page_title}=    Run Keyword If    ${status}==True    Get Title    ELSE    Set Variable    ${EMPTY}

    Sleep  3
    Take Os Screenshot  ${UTILS_ENDPOINT}  ${OUTPUT_DIR}${/}screenshot_${page_title}.png
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_WEB}   ${page_title}    ${OUTPUT_DIR}${/}screenshot_${page_title}.png

    Close Browser


Take Different Version Screenshots
    [Arguments]    ${url}
    
    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Add All Cookies From State  ${COOKIES_DIR}${/}cookies.json
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}  storageState=${COOKIES_DIR}${/}cookies.json
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}  storageState=${COOKIES_DIR}${/}cookies.json
        New Page  ${URL}
    END
    
    Sleep  2
    # Click    xpath=//button[contains(text(), 'Aceptar')]
    Set Viewport Size    375      667
    Sleep  3
    Take Screenshot  filename=${OUTPUT_DIR}${/}mobile_screenshot.png
    Set Viewport Size    768    1024
    Sleep  3
    Take Screenshot  filename=${OUTPUT_DIR}${/}ipad_screenshot.png
    Set Viewport Size    1280    800
    Sleep  3
    Take Screenshot  filename=${OUTPUT_DIR}${/}desktop_screenshot.png
    Close Browser

    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZO_WEB_MOVIL}   ${movil}     ${OUTPUT_DIR}${/}mobile_screenshot.png    width_inches=3.5
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZO_WEB_TABLETA}   ${tableta}     ${OUTPUT_DIR}${/}ipad_screenshot.png   width_inches=4
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZO_WEB_ESCRITORIO}   ${escritorio}     ${OUTPUT_DIR}${/}desktop_screenshot.png