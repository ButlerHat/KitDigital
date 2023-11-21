*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    OperatingSystem


*** Variables ***
${url}    https://djadelpeluqueria.es
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.txt
${ID_EXECUTION}  0
# ${is_WSENDPOINT}


*** Test Cases ***
Obtener Textos de Encabezados
    [Setup]   Crear Archivo si no existe
    
    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}
        New Page  ${URL}
    END

    wait until network is idle
    ${h1_elements}=    Get Elements    xpath=//h1
    ${h2_elements}=    Get Elements    xpath=//h2
    ${h3_elements}=    Get Elements    xpath=//h3
    FOR    ${element}    IN    @{h1_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},KitD_TextosH,PASS,,"H1 - ${text}"${\n}
    END
    FOR    ${element}    IN    @{h2_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},KitD_TextosH,PASS,,"H2 - ${text}"${\n}
    END
    FOR    ${element}    IN    @{h3_elements}
        Scroll To Element    ${element}
        Sleep  1
        ${text}=    Get Text    ${element}
        Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},KitD_TextosH,PASS,,"H3 - ${text}"${\n}
    END
    Close Browser


*** Keywords ***
Crear Archivo si no existe
    ${is_file}  Evaluate  bool(os.path.isfile("${RETURN_FILE}"))  modules=os
    IF  ${is_file}  RETURN  
    Create File    ${RETURN_FILE}
    Append To File    ${RETURN_FILE}  id_execution,robot,status,exception,msg${\n}
