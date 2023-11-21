*** Settings ***
Documentation  All good
Library       ButlerRobot.AIBrowserLibrary  stealth_mode=${True}  fix_bbox=${TRUE}  presentation_mode=${True}  console=${False}  record=${False}  WITH NAME  Browser
Library       OperatingSystem
Library       Collections
Library    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/KitD_Pantallazos/word_helper.py
Variables  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/robotframework/citaciones/utils/variables.py  ${info_file}


*** Variables ***
${URL}  https://www.donde-estamos.es/alta-empresa
# ${WSENDPOINT}  ws://192.168.85.2/playwright_94bacd4d-eb37-4a6d-86a2-54c6724dcb35/ws

${WORD_FILE}    /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/evidencias.docx
${SCREENSHOT_DIR}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueria.es/directories
${localidad_email}  jose.cartilagos@bluepath.es
${localidad_password}  pepe1234
${province_dondeestamos}  Madrid


# ${info_file}  /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital/result_kit/djadelpeluqueriaes/directories/company.json
# ${RETURN_FILE}  ${OUTPUT_DIR}${/}return_msg.csv  # columns: 1) ID_EXECUTION, 2) ROBOT, 3) STATUS, 4) EXCEPTION, 5) MESSAGE
# ${ID_EXECUTION}  0
# ${email}  jose.cortinas@bluepath.es
# ${username}    Torrejo 
# ${password}  calderascitation6
# ${keywords}  Calderas
# ${dondeestamos_province}  Madrid
# ${postal}  28850
# ${category_dondeestamos}  Servicios

# ${long_description}  Líderes en calderas y sistemas de calefacción. Calidad, eficiencia y confianza para tu hogar. ¡Calienta tus inviernos con nosotros!${\n}

# # From Json    
# ${website}  https://google.com
# ${phone}    666666666
# ${company_name}  Torrejon de Ardoz Calderas
# ${description}    Líderes en calderas y sistemas de calefacción. Calidad, eficiencia y confianza para tu hogar. ¡Calienta tus inviernos con nosotros!
# ${address}  Calle de la Constitución, 1, 28850 Torrejón de Ardoz, Madrid


*** Test Cases ***
Get Localidad
    [Tags]  get_localidad

    ${old_timeout}  Set Browser Timeout    60

    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}
        New Page  ${URL}
    END

    Run Keyword And Ignore Error  Accept cookies
    Type ${localidad_email} in email usuario
    Write ${localidad_password} in contraseña
    Click on login

    @{options}  Get Localidad from ${province_dondeestamos}
    ${options_no_commas}  Evaluate  "${options}".replace(',', ';')
    
    Log  ${options}  console=${True}
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,PASS,,${options_no_commas}${\n}


dondeestamos
    [Tags]  dondeestamos
    # ${username}  Evaluate  f'${username}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'  modules=random

    ${old_timeout}  Set Browser Timeout    60

    ${variables}  Get Variables
    ${is_WSENDPOINT}   Evaluate   "\${WSENDPOINT}" in $variables
    IF  ${is_WSENDPOINT} == True
        # Para Prod
        TRY
            Connect To Browser Over Cdp    ${WSENDPOINT}
            Go To  ${URL}
        EXCEPT
            Connect To Browser    ${WSENDPOINT}
            New Context  viewport=${None}
            New Page  ${URL}
        END
    ELSE
        # Para Dev
        New Browser  chromium  headless=${False}
        New Context  viewport=${None}
        New Page  ${URL}
    END

    Run Keyword And Ignore Error  Accept cookies
    Click on registrarse
    Write ${username} in nombre de usuario
    Write ${email} in email
    Type ${password} in password
    Type ${password} in repeat password
    Submit

    Comment  Email in use
    TRY
        Get Element  //*[@id='business_name']
    EXCEPT
        # Check if usuario ya esta en uso
        ${el_usuario}  Get Element Count  //li[contains(text(),'usuario ya')]
        IF  ${el_usuario} > 0   Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,FAIL,VariableError:username,El usuario ya está usado en donde-estamos.es${\n}
        
        # Check if email ya esta en uso
        ${el_email}  Get Element Count  //li[contains(text(),'correo ya')]
        IF  ${el_email} > 0   Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,FAIL,VariableError:email,El correo ya está usado en donde-estamos.es${\n}

        Fail  Usuario no creado
    END

    Click on alta gratuita

    Input ${company_name} in nombre de la empresa
    Select ${category_dondeestamos} in categoria
    Input ${keywords} in Actividad
    Select ${dondeestamos_province.split("-")[0].strip()} in localidad
    Input ${address} in direccion
    Input ${postal} in codigo postal
    Write ${phone} in telefono
    Input ${email} in email
    Write ${website} in web
    Type ${long_description} in descripcion
    Click on grabar datos de la empresa

    ${url_result}  Get Url
    IF  "${url_result}" == "https://www.donde-estamos.es/alta-empresa"
        Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,FAIL,,No se ha podido obtener la url${\n}
        Fail  Empresa no creada
    END

    Log  Empresa creada: ${url_result}
    
    Go To  ${url_result}
    Run Keyword And Ignore Error  Wait Until Network Is Idle
    Run Keyword And Ignore Error  Scroll To Element    //*h4*[contains(text(),'${company_name}')]
    Take Screenshot  filename=${SCREENSHOT_DIR}${/}dondeestamos.png
    
    Append Text And Picture To Document    ${WORD_FILE}  {PANTALLAZOS_DIRECTORIOS}   Donde estamos: ${url_result}   ${SCREENSHOT_DIR}${/}dondeestamos.png
    Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,PASS,,URL:${url_result}|SCREENSHOT:${SCREENSHOT_DIR}${/}dondeestamos.png${\n}

*** Keywords ***

Accept cookies
    Browser.Click  //a[@class='cc-btn cc-dismiss']

Click on registrarse
    Browser.Click  //a[contains(@class, 'btn-info')]

Type ${localidad_email} in email usuario
    Browser.Click  //*[@id="username"]
    Browser.Keyboard Input    type    ${localidad_email}

Write ${localidad_password} in contraseña
    Browser.Click  //*[@id="password"]
    Browser.Keyboard Input    type    ${localidad_password}

Click on login
    Browser.Click  //*[@id="_submit"]

Get Localidad from ${province_dondeestamos}
    [Tags]  no_record
    Browser.Click  //*[@id='business_city']/../span[1]
    FOR  ${i}  IN RANGE  5
        TRY
            Wait For Elements State    //*[@id='business_city']/../span[1]//span[@aria-expanded='true']  visible  1s
            BREAK
        EXCEPT
            Browser.Click  //*[@id='business_city']/../span[1] 
        END
    END
    Browser.Keyboard Input    type    ${province_dondeestamos}
    Wait For Elements State    //ul[@id='select2-business_city-results']//*[contains(text(),'Buscando')]  visible
    Wait For Elements State    //ul[@id='select2-business_city-results']//*[contains(text(),'Buscando')]  hidden
    @{provinces}  Get Elements  //ul[@id='select2-business_city-results'] 
    @{text_provinces}  Create List
    
    IF  len(${provinces}) == 0
        Log  No se ha encontrado la provincia ${province_dondeestamos}
        Append To File    ${RETURN_FILE}  ${\n}${ID_EXECUTION},dondeestamos,FAIL,VariableError:email,No hay localidades en ${province_dondeestamos}${\n}
        Fail  No se ha encontrado la provincia ${province_dondeestamos}
    END

    FOR  ${dondeestamos_province}  IN  @{provinces}
        ${text_province}  Get Text  ${dondeestamos_province}
        Append To List  ${text_provinces}  @{text_province.split('\n')}
    END

    RETURN  ${text_provinces}

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

Input ${company_name} in nombre de la empresa
    Browser.Click  //*[@id='business_name']
    Browser.Keyboard Input    type    ${company_name}
    
Select ${category_dondeestamos} in categoria
    Browser.Select Options By  //*[@id='business_sector']  label  ${category_dondeestamos}

Input ${keywords} in Actividad
    Browser.Click  //*[@id='business_activity']
    Browser.Keyboard Input    type    ${keywords}

Select ${dondeestamos_province} in localidad
    Browser.Click  //*[@id='business_city']/../span[1]
    Sleep  1
    Browser.Keyboard Input    type    ${dondeestamos_province}
    Browser.Click  (//*[@id='select2-business_city-results']//b[contains(text(),'${dondeestamos_province}')])[1]

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

Type ${long_description} in descripcion
    Browser.Click  //*[@id='business_comments']
    Browser.Keyboard Input    type    ${long_description}

Click on grabar datos de la empresa
    Browser.Click  //button[@type='submit']