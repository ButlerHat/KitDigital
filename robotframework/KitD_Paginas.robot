*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    OperatingSystem


*** Variables ***
${URL}    https://panaderiajesus.com/#/es
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${MAX_DEPTH}  1
${ID_EXECUTION}  0
${FILTER_ENDING}  ${True}
${WSENDPOINT}  ws://192.168.85.2/playwright_ee7f6592-5455-4939-b4b0-a167fa05bcb6/devtools/browser/632d208c-aba2-4592-a936-647799a225e3


*** Test Cases ***

Obtener URLs de la Página Principal
    [Setup]   Crear Archivo si no existe
    TRY
        Connect To Browser Over Cdp    ${WSENDPOINT}
    EXCEPT
        TRY
            Connect To Browser    ${WSENDPOINT}
        EXCEPT
            Log  In local is not necessary to connect to browser
        END
    END
        
    Crawl Site    ${URL}  max_depth_to_crawl=${MAX_DEPTH}   page_crawl_keyword=Miaccion

*** Keywords ***
Miaccion
    ${url}=       Get Url
    ${is_file}  Evaluate  bool("${url.split("/")[-1]}")
    IF  ${is_file} and ${FILTER_ENDING}  RETURN  
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},KitD_Paginas,PASS,,"${url}"${\n}

Crear Archivo si no existe
    ${is_file}  Evaluate  bool(os.path.isfile("${RETURN_FILE}"))  modules=os
    IF  ${is_file}  RETURN  
    Create File    ${RETURN_FILE}
    Append To File    ${RETURN_FILE}  id_execution,robot,status,exception,msg${\n}
