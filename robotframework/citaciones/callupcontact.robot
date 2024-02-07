*** Settings ***
Documentation  All good
Library       ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${False}  WITH NAME  Browser
Library       OperatingSystem
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py
Variables     /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/citaciones/utils/variables.py  ${info_file}


*** Variables ***
${URL}  https://www.callupcontact.com/active/register/register.php?
# ${WSENDPOINT}  # ws://localhost:9222/devtools/browser/1b5b309b37e0231099f023aa9e96de0b

${CAPTCHA_API_KEY}  1b5b309b37e0231099f023aa9e96de0b
# ${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/evidencias.docx
# ${SCREENSHOT_DIR}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/directories

# ${info_file}  /tmp/last_company_k2.json
# ${email}  ventcal@bluepath.es
# ${name}    Ventcal
# ${surname}    Torrejo 
# ${password}  calderascitation6
# ${cif}  39832477L
${country}  Spain  # English
# ${keywords}  Calderas
# ${province}  Madrid

# From Json
# ${website}
# ${phone}
# ${company_name}
# ${description}
# ${address}


*** Test Cases ***
callupcontact
    [Tags]  callupcontact

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

    Write ${name} at Name   ${name}
    Write ${email} at Email  ${email}
    Write ${password} at Password  ${password}
    Write ${country} at Country  ${country}
    Click on registrar
    Write ${company_name} at Business Name  ${company_name}
    Write ${keywords} at Keywords  ${keywords}
    Write ${province} at Province  ${province}
    Write ${description} at Description  ${description}
    Write ${phone} at Phone  ${phone}
    Write ${email} at Email Communication  ${email}
    Write ${website} at Website  ${website}
    Write ${address} at Street1  ${address}
    Click at find address
    Click at Next

    ${url_result}  Get Href of Work Group
    Log  Empresa ${company_name} creada en ${url_result}  console=${True}
    
    Go To  ${url_result}
    Run Keyword And Ignore Error  Wait Until Network Is Idle
    Set Viewport Size  1920  1080
    Run Keyword And Ignore Error  Scroll By  vertical=100%
    Run Keyword And Ignore Error  Scroll To Element  //div[@class='content']
    # Consent cookies
    Run Keyword And Ignore Error  Click on consent cookies
    Take Screenshot  filename=${SCREENSHOT_DIR}${/}callupcontact.png
    
    # Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_DIRECTORIOS}   Callupcontact: ${url_result}    ${SCREENSHOT_DIR}${/}callupcontact.png
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},callupcontact,PASS,,"URL:${url_result}|SCREENSHOT:${SCREENSHOT_DIR}${/}callupcontact.png"${\n}


*** Keywords ***

Click on consent cookies
    Browser.Click  //button/*[text()='Consent']

Write ${name} at Name
    [Arguments]   ${name}
    Browser.Type Text    xpath=//input[@name="name"]    ${name}

Write ${email} at Email
    [Arguments]   ${email}
    Browser.Type Text    xpath=//input[@name="user"]    ${email}

Write ${password} at Password
    [Arguments]   ${password}
    Browser.Type Text    xpath=//input[@name="pwd"]    ${password}

Write ${country} at Country
    [Arguments]   ${country}
    Browser.Type Text    xpath=//input[@placeholder="Country search"]    ${country}
Click on registrar
    Browser.Click    xpath=//input[@name="submit"]

Write ${company_name} at Business Name
    [Arguments]   ${company_name}
    Browser.Type Text    xpath=//input[@name="first_name"]    ${company_name}

Write ${keywords} at Keywords
    [Arguments]   ${keywords}
    Browser.Type Text    xpath=//input[@name="keywords"]    ${keywords}

Write ${province} at Province
    [Arguments]   ${province}
    Browser.Type Text    xpath=//input[@name="region"]    ${province}

Write ${description} at Description
    [Arguments]   ${description}
    Browser.Type Text    xpath=//textarea[@name="description"]    ${description}

Write ${phone} at Phone
    [Arguments]   ${phone}
    Browser.Type Text    xpath=//input[@name="mobile"]    ${phone}    

Write ${email} at Email Communication
    [Arguments]   ${email}
    Browser.Type Text    xpath=//input[@name="email"]    ${email}

Write ${web} at Website
    [Arguments]   ${web}
    Browser.Type Text    xpath=//input[@name="website"]    ${web}

Write ${address} at Street1
    [Arguments]   ${address}
    Browser.Type Text    xpath=//input[@name="street1"]    ${address}

Click at find address
    Browser.Click    xpath=//button[@id="geo1"]

Click at Next
    Browser.Click    xpath=(//input[@name="update"])[2]

Get Href of Work Group
    ${url_result}  Get Attribute    (//tr[contains(.,"Work")])[last()]//a    href
    RETURN  https://www.callupcontact.com/${url_result}