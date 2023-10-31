*** Settings ***
Documentation  All good
Library       ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${False}  WITH NAME  Browser
Variables  /workspaces/robotframework/dev/spider_repo/Utils/variables.py  ${info_file}


*** Variables ***
${CAPTCHA_API_KEY}  1b5b309b37e0231099f023aa9e96de0b
${info_file}  /tmp/last_company_k2.json
# ${email}  ventcal@bluepath.es
# ${name}    Ventcal
# ${surname}    Torrejo 
# ${password}  calderascitation6
# ${cif}  39832477L
${country}  Spain  # English
${keywords}  Calderas
# ${province}  Madrid

# From Json
# ${website}
# ${phone}
# ${company}
# ${description}
# ${address}


*** Test Cases ***
callupcontact
    Browser.New Browser  chromium  headless=${False}
    Browser.New Context
    Browser.New Page  url=https://www.callupcontact.com/active/register/register.php?

    Write ${name} at Name   ${name}
    Write ${email} at Email  ${email}
    Write ${password} at Password  ${password}
    Write ${country} at Country  ${country}
    Click on registrar
    Write ${company} at Business Name  ${company}
    Write ${keywords} at Keywords  ${keywords}
    Write ${province} at Province  ${province}
    Write ${description} at Description  ${description}
    Write ${phone} at Phone  ${phone}
    Write ${email} at Email Communication  ${email}
    Write ${website} at Website  ${website}
    Write ${address} at Street1  ${address}
    Click at find address
    Click at Next

    ${url}  Get Href of Work Group
    Log  Empresa ${company} creada en ${url}  console=${True}


*** Keywords ***

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

Write ${company} at Business Name
    [Arguments]   ${company}
    Browser.Type Text    xpath=//input[@name="first_name"]    ${company}

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
    ${url}  Get Attribute    (//tr[contains(.,"Work")])[last()]//a    href
    RETURN  https://www.callupcontact.com/${url}