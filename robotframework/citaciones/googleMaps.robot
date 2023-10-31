*** Settings ***
Library       ButlerRobot.AIBrowserLibrary  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${True}  WITH NAME  Browser
Library       OperatingSystem
Library       /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/citaciones/file_manager.py

*** Variables ***
${url}  https://goo.gl/maps/tkixTKKXDf1qACjv5


${info_file}  /tmp/last_company_k2.json

${email}  k2energia@bluepath.es
${name}    K2
${surname}    Calderas
# Password must be at least 10 characters 
${password}  calderascitation9
${cif}  G32309361  
${nif}  39470152J
${country}  Spain  # English callup
${categorybiz}  Professional Services
${categorynext}  Business Support, Supplies and Services
${category_cylex}  Calefacción
${categoryfour}  Servicios Comerciales y profesionales
${categoryinfo}  Reparación calderas
${categoryprovenexpert}  Servicios
${categoryyellow}  Servicio de reparación
${categoryhotfrog}  Consumer Electronics Repair
${category_dondeestamos}  Servicios
${categoryeuropages}    Calderas domésticas
${activity_europepages}  Proveedor de servicios
${city}  Torrejón de Ardoz
${postal}  28023
${keywords}  Calderas
${province}  Madrid
${username}  k2bp  # Debe ser unica
${120char_description}  Líderes en calderas y sistemas de calefacción. Calidad, eficiencia y confianza para tu hogar. ¡Calienta tus inviernos con nosotros!${\n}
${day}  12
${month}  12
${year}  1990
${logo}  /workspaces/robotframework/dev/spider_repo/Robots/citaciones/static/IMG-20220117-WA0002.jpg



*** Test Cases ***
ReadFromMaps
    ${username}  Evaluate  f'${username}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'  modules=random

    New Browser    chromium    headless=${False}
    New Context    storageState=/workspaces/robotframework/dev/spider_repo/Robots/citaciones/cookies.json
    New Page    url=${url}
    Log To Console    message=URL: ${url}

    ${company}  Get Title
    Log To Console    message=Company: ${company}
    ${address}  Get address
    Log To Console    message=Address: ${address}
    ${website}  Get website
    Log To Console    message=Website: ${website}
    ${phone}  Get phone
    Log To Console    message=Phone: ${phone}
    ${description}  Get description
    Log To Console    message=Description: ${description}

    Close Browser

    ${company_dict}  Create Dictionary  company=${company}  
    ...  address=${address}  
    ...  website=${website}  
    ...  phone=${phone}  
    ...  description=${description}
    ...  info_file=${info_file}
    ...  email=${email}
    ...  name=${name}
    ...  surname=${surname}
    ...  password=${password}
    ...  cif=${cif}
    ...  nif=${nif}
    ...  categorybiz=${categorybiz}
    ...  categorynext=${categorynext}
    ...  category_cylex=${category_cylex}
    ...  categoryfour=${categoryfour}
    ...  categoryinfo=${categoryinfo}
    ...  categoryprovenexpert=${categoryprovenexpert}
    ...  categoryyellow=${categoryyellow}
    ...  categoryhotfrog=${categoryhotfrog}
    ...  category_dondeestamos=${category_dondeestamos}
    ...  categoryeuropages=${categoryeuropages}
    ...  activity_europepages=${activity_europepages}
    ...  city=${city}
    ...  postal=${postal}
    ...  keywords=${keywords}
    ...  province=${province}
    ...  country=${country}
    ...  username=${username}
    ...  120char_description=${120char_description}
    ...  day=${day}
    ...  month=${month}
    ...  year=${year}
    ...  logo=${logo}
    
    Store Data  ${company_dict}  ${info_file}

    ${company_restored}  Restore Data    ${info_file}
    Log To Console    message=Company restored: ${company_restored}



*** Keywords ***
Get Title
    ${company}   Browser.Get Text  xpath=//h1
    RETURN  ${company}

Get address
    ${address}  Browser.Get Text    xpath=//button[@data-item-id="address"]//div[text()]
    RETURN  ${address}

Get website
    ${result}  Browser.Get Element Count    xpath=//a[@data-item-id="authority"]//div[text()]
    IF  ${result} != 0
        ${website}  Browser.Get Text    xpath=//a[@data-item-id="authority"]//div[text()]
    ELSE
        ${website}  Set Variable    www.no_website.com
    END
    RETURN  ${website}

Get phone
    ${phone}  Browser.Get Text  xpath=//button[contains(@data-item-id,"phone:")]//div[text()]
    RETURN  ${phone}

Get description
    ${info_sections}  Browser.Get Element Count  xpath=//div[contains(@aria-label,"Información")]
    IF  "${info_sections}"=="2"
        ${description}  Browser.Get Text    xpath=(//div[contains(@aria-label,"Información")][1]//div[text()])[1]
    ELSE
        ${description}  Set Variable    No info
    END
    RETURN  ${description}


    