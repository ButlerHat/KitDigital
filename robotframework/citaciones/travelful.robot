*** Settings ***
Documentation  Funciona perfecto
Library       ButlerRobot.AIBrowserLibrary  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${True}  WITH NAME  Browser
Variables      /workspaces/robotframework/dev/spider_repo/Utils/variables.py  ${info_file}


*** Variables ***
${info_file}  /tmp/last_company_k2.json
# ${email}  calderea@bluepath.es
# ${username}  caldereabp  # Debe ser unica
# ${password}  calderascitation5
# ${city}  Madrid
${country}  Spain

# ${company}  # Debe ser unica
# ${address}
# ${website}
# ${phone}


*** Test Cases ***
travelful
    ${username}  Evaluate  f'${username}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'  modules=random

    Browser.New Stealth Persistent Context  browser=chromium  headless=${False}  url=http://www.travelful.net/register.asp
    Write ${username} at Nombre
    Write ${email} at Email
    Write ${password} at Password
    Write ${password} at Confirm password
    Click at Register
    Click at Add a location
    Write ${company} at Name
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
    ${url}  Get public url
    Log  La empresa se ha creado correctamente: ${url}	console=${True}	


*** Keywords ***

Get public url
    ${url}  Get Url
    RETURN  ${url}
    
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

Write ${company} at Name
    Browser.Type Text    xpath=//input[@id="title"]    ${company}

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