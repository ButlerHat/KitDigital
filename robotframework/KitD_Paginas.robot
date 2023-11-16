*** Settings ***
Library    ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  record=${False}  console=${False}  presentation_mode=${True}  WITH NAME  Browser 
Library    OperatingSystem


*** Variables ***
${URL}    https://panaderiajesus.com/#/es
${RETURN_FILE}  ${OUTPUT_DIR}${/}msg.csv
${MAX_DEPTH}  1
${ID_EXECUTION}  0
${FILTER_ENDING}  ${True}


*** Test Cases ***

Obtener URLs de la Página Principal
       [Setup]   Crear Archivo si no existe
       Crawl Site    ${URL}  max_depth_to_crawl=${MAX_DEPTH}   page_crawl_keyword=Miaccion

*** Keywords ***
Miaccion
    ${url}=       Get Url
    ${is_file}  Evaluate  bool("${url.split("/")[-1]}")
    IF  ${is_file} and ${FILTER_ENDING}  RETURN  
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},KitD_Paginas,PASS,,${url}${\n}

Crear Archivo si no existe
    ${is_file}  Evaluate  bool(os.path.isfile("${RETURN_FILE}"))  modules=os
    IF  ${is_file}  RETURN  
    Create File    ${RETURN_FILE}
    Append To File    ${RETURN_FILE}  id_execution,robot,status,exception,msg${\n}
