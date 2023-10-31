*** Settings ***
Documentation  All good
Library       ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${False}  WITH NAME  Browser
Variables  /workspaces/robotframework/dev/spider_repo/Utils/variables.py  ${info_file}


*** Variables ***
${info_file}  /tmp/last_company_prueba.json
${email}  jose.cortes@bluepath.es
# ${username}    Torrejo 
# ${password}  calderascitation6
# ${keywords}  Calderas
# ${province}  Madrid
# ${postal}  28850
# ${category_dondeestamos}  Servicios

# ${120char_description}  Líderes en calderas y sistemas de calefacción. Calidad, eficiencia y confianza para tu hogar. ¡Calienta tus inviernos con nosotros!${\n}

# From Json
# ${website}
# ${phone}
# ${company}
# ${description}
# ${address}


*** Test Cases ***
dondeestamos
    ${username}  Evaluate  f'${username}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'  modules=random
    
    Browser.New Browser  chromium  headless=${False}
    Browser.New Context
    Browser.New Page  url=https://www.donde-estamos.es/alta-empresa

    Run Keyword And Ignore Error  Accept cookies
    Click on registrarse
    Write ${username} in nombre de usuario
    Write ${email} in email
    Type ${password} in password
    Type ${password} in repeat password
    Submit

    Click on alta gratuita
    Scroll By  vertical=100%
    Input ${company} in nombre de la empresa
    Select ${category_dondeestamos} in categoria
    Input ${keywords} in Actividad
    Select ${province} in localidad
    Input ${address} in direccion
    Input ${postal} in codigo postal
    Scroll By  vertical=100%
    Write ${phone} in telefono
    Input ${email} in email
    Write ${website} in web
    Scroll By  vertical=100%
    Type ${120char_description} in descripcion
    Click on grabar datos de la empresa

    ${url}  Get Url
    Log  Empresa creada: ${url}



*** Keywords ***

Accept cookies
    Browser.Click  //a[@class='cc-btn cc-dismiss']

Click on registrarse
    Browser.Click  //a[contains(@class, 'btn-info')]

Write ${username} in nombre de usuario
    Browser.Click  //*[@id='fos_user_registration_form_username']
    Browser.Keyboard Input    type    ${username}

Write ${email} in email
    Browser.Click  //*[@id='fos_user_registration_form_email']
    Browser.Keyboard Input    type    ${email}

Type ${password} in password
    Browser.Click  //*[@id='fos_user_registration_form_plainPassword_first']
    Browser.Keyboard Input    type    ${password}

Type ${password} in repeat password
    Browser.Click  //*[@id='fos_user_registration_form_plainPassword_second']
    Browser.Keyboard Input    type    ${password}

Submit
    Browser.Click  //button[@type='submit']

Click on alta gratuita
    Browser.Click  //a[text()='Alta gratuita']

Input ${company} in nombre de la empresa
    Browser.Click  //*[@id='business_name']
    Browser.Keyboard Input    type    ${company}
    
Select ${category_dondeestamos} in categoria
    Browser.Select Options By  //*[@id='business_sector']  label  ${category_dondeestamos}

Input ${keywords} in Actividad
    Browser.Click  //*[@id='business_activity']
    Browser.Keyboard Input    type    ${keywords}

Select ${province} in localidad
    Browser.Click  //*[@id='business_city']/../span[1]
    Sleep  1
    Browser.Keyboard Input    type    ${province}
    Browser.Click  (//*[@id='select2-business_city-results']//b[contains(text(),'${province}')])[1]

Input ${address} in direccion
    Browser.Click  //*[@id='business_address']
    Browser.Keyboard Input    type    ${address}

Input ${postal} in codigo postal
    Browser.Click  //*[@id='business_postalCode']
    Browser.Keyboard Input    type    ${postal}

Write ${phone} in telefono
    Browser.Click  //*[@id='business_phone']
    Browser.Keyboard Input    type    ${phone}

Input ${email} in email
    Browser.Click  //*[@id='business_email']
    Browser.Keyboard Input    type    ${email}

Write ${website} in web
    Browser.Click  //*[@id='business_web']
    Browser.Keyboard Input    type    ${website}

Type ${120char_description} in descripcion
    Browser.Click  //*[@id='business_comments']
    Browser.Keyboard Input    type    ${120char_description}

Click on grabar datos de la empresa
    Browser.Click  //button[@type='submit']