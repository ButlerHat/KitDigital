Navegar a la url de la página
Con la librería dialogs (https://robotframework.org/robotframework/latest/libraries/Dialogs.html), hacer un paso manual donde se selecciones el idioma manualmente dentro de la página.
Con las URLs de la página navegar a todas y hacer los pantallazos como en la tarea 5


*** Settings ***
Library    SeleniumLibrary
Library    word_helper.py
Library    Dialogs
Library    Browser
Library    OperatingSystem

*** Variables ***
${url1}    https://djadelpeluqueria.es/
#${url2}    https://djadelpeluqueria.es/blog/
#${url3}    https://djadelpeluqueria.es/servicios/
#${url4}    https://djadelpeluqueria.es/contacto/
#${url5}    https://djadelpeluqueria.es/galeria-de-fotos/
#${url6}    https://djadelpeluqueria.es/acerca-de/

@{urls}    ${url1}  
${WORD_FILE}    WebIdioma.docx
${Aceptar}   Aceptar
${Accept}    Accept
    
*** Test Cases ***
Get Title Screenshots and versions for URLs
    Create New Document    ${WORD_FILE}
    SeleniumLibrary.Open Browser    ${url1}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer 
    Click Element    xpath=//button[contains(text(), 'Aceptar')]

    Pause Execution    Cambia el idioma, luego pulsa OK para continuar.

    
    ${current_url}=    Get Location

    Crawl Site    ${current_url}    max_depth_to_crawl=1    page_crawl_keyword=Miaccion

    SeleniumLibrary.Close All Browsers

    

*** Keywords *** 
Miaccion
    ${url}=    Get Url
    SeleniumLibrary.Open Browser    ${url}    browser=chrome
    ${status}=    Run Keyword And Return Status    SeleniumLibrary.Get Title
    
    IF    '${status}' == 'False'
        SeleniumLibrary.Close Browser
        Return From Keyword
    END

    ${page_title}=   SeleniumLibrary.Get Title 
   
    IF  '${url}' == '${url1}' or 'Page Not Found' in '${page_title}'
        SeleniumLibrary.Close Browser
        Return From Keyword
    END


    ${is_file}  Evaluate  bool("${url.split("/")[-1]}")
    
    IF  ${is_file}  
        SeleniumLibrary.Close Browser
        Return From Keyword
    END 
    
    Open URL and Get Info    ${url}
    
    SeleniumLibrary.Close Browser



Open URL and Get Info
    [Arguments]    ${url}
    #SeleniumLibrary.Open Browser    ${url}    browser=chrome
    Wait Until Page Contains Element    xpath=//footer 
    Click Element    xpath=//button[contains(text(), '${Accept}')]


    ${status}=    Run Keyword And Return Status    SeleniumLibrary.Get Title
    ${page_title}=    Run Keyword If    ${status}==True    SeleniumLibrary.Get Title    ELSE    Set Variable    ${EMPTY}

    Capture Page Screenshot    screenshot.png
    Append Text And Picture To Document    ${WORD_FILE}    ${page_title}    screenshot.png

  

