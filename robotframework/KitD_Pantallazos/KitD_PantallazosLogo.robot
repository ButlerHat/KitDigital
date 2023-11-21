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
Library    OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py


*** Variables ***
${url}    https://djadelpeluqueria.es/

# ${COOKIES_DIR}   /tmp/djadelpeluqueria


*** Test Cases ***
Open URL and Get Info
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

    ${STATUS}  ${MSG}  Run Keyword And Ignore error  Wait For Elements State    xpath=//footer  visible  timeout=5s
    Sleep  2
    IF  '${STATUS}'=='PASS'  
        Scroll TO Element  //footer
    ELSE
        Scroll By  vertical=100%
    END
    # Leave browser open to capture os screenshot

