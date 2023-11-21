*** Settings ***
Documentation  Funciona perfecto
Library       ButlerRobot.AIBrowserLibrary  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${False}  WITH NAME  Browser
Library       OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py
Variables      /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/citaciones/utils/variables.py  ${info_file}


*** Variables ***
${URL}  http://www.travelful.net/register.asp
# ${WSENDPOINT}

${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/evidencias.docx
${SCREENSHOT_DIR}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/directories

${info_file}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueriaes/directories/company.json
# ${RETURN_FILE}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/travelful/msg.csv
# ${email}  calderea@bluepath.es
# ${username}  caldereabp  # Debe ser unica
# ${password}  calderascitation5
# ${city}  Madrid
${country}  Spain

# ${company_name}  # Debe ser unica
# ${address}
# ${website}
# ${phone}


*** Test Cases ***
travelful
    [Tags]  travelful
    # ${username}  Evaluate  f'${username}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'  modules=random

    # Browser.New Stealth Persistent Context  userDataDir=/tmp/travelful  browser=chromium  headless=${False}  url=http://www.travelful.net/register.asp

    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context
        New Page  ${URL}
    END
    
    Write ${username} at Nombre
    Write ${email} at Email
    Write ${password} at Password
    Write ${password} at Confirm password
    Click at Register

    TRY
        Wait For Elements State    xpath=//a[text()="Add a location »"]  visible  timeout=10s
    EXCEPT
        # Get message this user already exists
        ${el_user}  Get Element Count    //span[contains(text(), "user")][contains(text(), "exists")]
        
        IF  ${el_user} > 0   Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},travelful,FAIL,VariableError:username,"El usuario ${username} ya está usado en travelful.net"${\n}
        Fail  El usuario ya está usado en travelful.net
    END

    Click at Add a location
    Write ${company_name} at Name
    Write ${address} at Address
    Write ${city} at City
    Write ${country} at Country
    Write ${website} at Website
    Write ${phone} at Phone
    Sleep    1s
    Click at No share
    Sleep    1s
    Click at Save changes
    Sleep  1
    ${url_result}  Get public url
    Log  La empresa se ha creado correctamente: ${url_result}	console=${True}	
    
    Go To  ${url_result}
    Run Keyword And Ignore Error  Wait Until Network Is Idle
    Take Screenshot  filename=${SCREENSHOT_DIR}${/}travelful.png
    
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_DIRECTORIOS}   Travelful: ${url_result}    ${SCREENSHOT_DIR}${/}travelful.png
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},travelful,PASS,,"URL:${url_result}|SCREENSHOT:${SCREENSHOT_DIR}${/}travelful.png"${\n}


*** Keywords ***

Get public url
    ${url_result}  Get Url
    RETURN  ${url_result}
    
Write ${username} at Nombre
    Browser.Type Text    xpath=//input[@id="username"]    ${username}

Write ${email} at Email
    Browser.Type Text    xpath=//input[@id="email"]    ${email}

Write ${password} at Password
    Browser.Type Text    xpath=//input[@id="password"]    ${password}

Write ${password} at Confirm password
    Browser.Type Text    xpath=//input[@id="repassword"]    ${password}

Click at Register
    Browser.Click    xpath=//input[@type="submit"]

Click at Add a location
    Browser.Click    xpath=//a[text()="Add a location »"]

Write ${company_name} at Name
    Browser.Type Text    xpath=//input[@id="title"]    ${company_name}

Write ${address} at Address
    Browser.Type Text    xpath=//input[@id="formatted_address"]    ${address}

Write ${city} at City
    Browser.Type Text    xpath=//input[@id="city"]    ${city}

Write ${country} at Country
    Browser.Type Text    xpath=//input[@id="country"]    ${country}

Write ${website} at Website
    Browser.Clear Text    xpath=//input[@id="website"]
    Browser.Type Text    xpath=//input[@id="website"]    ${website}

Write ${phone} at Phone
    Browser.Type Text    xpath=//input[@id="phone"]    ${phone}

Click at No share
    Browser.Click    xpath=//input[@name="noshare"]
Click at Save changes
    Browser.Click    xpath=(//input[@value="Save changes"])[2]