*** Settings ***
Library    Browser
Library    OperatingSystem

*** Variables ***
${URL}    https://djadelpeluqueria.es/
${OUTPUT_FILE}  misurls.txt
${MAX_DEPTH}  1



*** Test Cases ***

Obtener URLs de la Página Principal
       [Setup]   Borrar el archivo
       Crawl Site    ${URL}  max_depth_to_crawl=${MAX_DEPTH}   page_crawl_keyword=Miaccion

*** Keywords ***
Miaccion
    ${url}=       Get Url
    ${is_file}  Evaluate  bool("${url.split("/")[-1]}")
    IF  ${is_file}  RETURN  
    Append To File    ${OUTPUT_FILE}    ${url}${\n}

Borrar el archivo
     Remove File    ${OUTPUT_FILE}
