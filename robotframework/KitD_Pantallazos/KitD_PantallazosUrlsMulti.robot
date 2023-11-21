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
Library    Dialogs
Library    OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py

*** Variables ***
# ${URL}  https://www.djadelpeluquero.com/
${WSENDPOINT}  ws://192.168.85.2/playwright_6cfa552a-53e0-4733-914d-5d3785b27018/devtools/browser/2a5daef8-f9fb-4e75-acda-16c557a4f865
# ${UTILS_ENDPOINT} 

${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${ID_EXECUTION}  0
${COOKIES_DIR}   /tmp/djadelpeluqueria
${WORD_FILE_TEMPLATE}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/Plantilla.docx
${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/PlantillaPelu.docx


*** Test Cases ***

Open URL and Get Info
    [Tags]  1

    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Add All Cookies From State    ${COOKIES_DIR}${/}cookies.json
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

    # Record one click and leave the page open
    # Record Click


Store URL
    [Tags]  2
    TRY
        Connect To Browser Over Cdp    ${WSENDPOINT}
    EXCEPT
        Connect To Browser    ${WSENDPOINT}
    END
    
    ${status}=    Run Keyword And Return Status    Get Title
    ${page_title}=    Run Keyword If    ${status}==True    Get Title    ELSE    Set Variable    ${EMPTY}

    TRY
        ${old_timeout}  Set Browser Timeout    1
        Take Os Screenshot  ${UTILS_ENDPOINT}  ${OUTPUT_DIR}${/}screenshot_${page_title}.png
    EXCEPT
        ${pages}  Get Page Ids
        Switch Page    ${pages[-1]}
        Take Os Screenshot  ${UTILS_ENDPOINT}  ${OUTPUT_DIR}${/}screenshot_${page_title}.png
    FINALLY
        Set Browser Timeout    ${old_timeout}
    END
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_MULTI-IDIOMA}   ${page_title}    ${OUTPUT_DIR}${/}screenshot_${page_title}.png

    # Close Page
    Append To File    ${RETURN_FILE}    ${\n}${ID_EXECUTION},KitD_PantallazosUrls.robot,PASS,,${URL}${\n}

