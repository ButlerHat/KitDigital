import datetime
import asyncio
import json
import os
import random
import pandas as pd
import numpy as np
import streamlit as st
import utils.robot_handler as robot_handler
from kitdigital import KitDigital, Stage, StageStatus, StageType
from utils.notifications import send_contact_to_ntfy



VARIABLES_DONDE_ESTAMOS = [
    "email",
    "username",
    "password",
    "keywords",
    "province",
    "postal",
    "category_dondeestamos",
    "long_description",
    "website",
    "phone",
    "company_name",
    "description",
    "address"
]

VARIABLES_CALLUPCONTACT = [
    "email",
    "name",
    "surname",
    "password",
    "cif",
    "country",
    "keywords",
    "province",
    "website",
    "phone",
    "company_name",
    "description",
    "address"
]

VARIABLES_TRAVELFULL = [
    "email",
    "username",
    "password",
    "city",
    "country",
    "company_name",
    "address",
    "website",
    "phone"
]


def get_robot_variables(kit_digital: KitDigital, dondeestamos_province: str) -> dict:
    """
    Get variables from excel, from state of kit_digital or from form.
    """
    company_data = {}
    # Create dataframe with default email, username, name, surname, password
    id_ = kit_digital.id.split(".")[0]
    default_data = {
        "email": f"agente_{id_}@bluepath.es",
        "username": f"agente_digitalizador_{id_}",
        "name": f"{id_}",
        "surname": "Agente",
        "password": f"{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}_{id_}"
    }
    df = pd.DataFrame([default_data])
    dir_stage = kit_digital.stages[StageType.DIRECTORIES]

    # GET FROM EXCEL
    # Download template
    st.markdown('---')
    st.markdown("### Plantilla para los datos")
    excel_template_path = st.secrets.paths.excel_template
    with open(excel_template_path, 'rb') as f:
        st.download_button(
            label="Descargar plantilla",
            data=f,
            file_name="template_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    uploaded_file = st.file_uploader("Adjunta el Excel con la información de la empresa. Las columnas deben contener las claves del formulario en la primera fila.", 
                                     type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

    # GET FROM STATE
    elif "company_data" in dir_stage.info:
        df = pd.DataFrame([dir_stage.info["company_data"]])
    
    if df is not None:
        df.columns = [x.lower() for x in df.columns]
        # Remove usuario: and empresa: from columns
        df.columns = [x.split(":")[1].strip() if ":" in x else x for x in df.columns]

    st.info("Subiendo el excel con la información, se rellenarán los campos del formulario automáticamente.")
       
    # GET FROM FORM
    st.markdown('---')
    st.markdown("### Datos para subir a los directorios")
    with st.form("Datos para subir a los directorios"):
        st.write("Proporciona los datos del usuario con el que registrarse")
        email_default = df['email'][0] if df is not None and 'email' in df.columns else ""
        email = st.text_input("Usuario: email", email_default, key="email")

        username_default = df['username'][0] if df is not None and 'username' in df.columns else ""
        username = st.text_input("Usuario: username", username_default, key="username")

        name_default = df['name'][0] if df is not None and 'name' in df.columns else ""
        name = st.text_input("Usuario: name", name_default, key="name")

        surname_default = df['surname'][0] if df is not None and 'surname' in df.columns else ""
        surname = st.text_input("Usuario: surname", surname_default, key="surname")

        password_default = df['password'][0] if df is not None and 'password' in df.columns else ""
        password = st.text_input("Usuario: password", type="password", value=password_default, key="password")
        repeat_password = st.text_input("Usuario: repeat password", type="password", value=password_default, key="repeat_password")

        st.write("Proporciona los datos de la empresa")
        company_name_default = df['company_name'][0] if df is not None and 'company_name' in df.columns else ""
        company_name = st.text_input("Empresa: company_name", company_name_default, key="company_name")

        address_default = df['address'][0] if df is not None and 'address' in df.columns else ""
        address = st.text_input("Empresa: address", address_default, key="address")

        website_default = df['website'][0] if df is not None and 'website' in df.columns else ""
        website = st.text_input("Empresa: website", website_default, key="website")

        phone_default = df['phone'][0] if df is not None and 'phone' in df.columns else ""
        phone = st.text_input("Empresa: phone", phone_default, key="phone")

        cif_default = df['cif'][0] if df is not None and 'cif' in df.columns else ""
        cif = st.text_input("Empresa: cif", cif_default, key="cif")

        country_default = df['country'][0] if df is not None and 'country' in df.columns else ""
        country = st.text_input("Empresa: country", country_default, key="country")

        province_default = df['province'][0] if df is not None and 'province' in df.columns else ""
        province = st.text_input("Empresa: province", province_default, key="province")

        dondeestamos_province = st.text_input("Empresa: province_dondeestamos. Si se desea cambiar, click en cambiar localidad arriba.", dondeestamos_province, key="province_dondeestamos", disabled=True)

        city_default = df['city'][0] if df is not None and 'city' in df.columns else ""
        city = st.text_input("Empresa: city", city_default, key="city")

        postal_default = df['postal'][0] if df is not None and 'postal' in df.columns else ""
        postal = st.text_input("Empresa: postal", postal_default, key="postal")

        sector_categories = ['Abogados', 'Aeronautica', 'Agropecuaria', 'Alimentación y bebidas', 'Animales', 'Arquitectura', 'Artes gráficas e Imprentas', 'Artesanía', 'Asesoría', 'Asociaciones profesionales', 'Audiovisuales', 'Automoción', 'Banca', 'Bazar', 'Carpinteria', 'Centros asistenciales', 'Centros Medicos', 'Cerrajerias', 'Climatizacion', 'Construcción e Inmobiliaria', 'Consultoria', 'Distribución', 'Electricidad', 'Electrodomésticos', 'Energias Renovables', 'Enseñanza', 'Envases y Embalajes', 'Equipamiento industrial', 'Extracciones minerales', 'Ferreterías', 'Fontanerías', 'Formación', 'Fumigación', 'Guarderias', 'Hostelería y Restauración', 'Hoteles', 'Industria', 'Informática y Electrónica', 'Ingeniería', 'Jugueterías', 'Laboratorios', 'Limpieza', 'Medio Ambiente', 'Metalurgia', 'Mobiliario y Decoración', 'Moda', 'Ocio infantil', 'Ocio y Deportes', 'Otros', 'Pinturas', 'Piscinas', 'Publicidad', 'Químico', 'Reciclados', 'Reciclaje', 'Salud y Belleza', 'Seguridad', 'Seguros', 'Servicios', 'Servicios públicos', 'Suministros Indsutriales', 'Telecomunicaciones', 'Transporte y Mensajería', 'Viajes', 'Viveros y plantas']
        category_dondeestamos = st.selectbox("Empresa: category_dondeestamos", sector_categories, key="category_dondeestamos")

        keywords_default = df['keywords'][0] if df is not None and 'keywords' in df.columns else ""
        keywords = st.text_input("Empresa: keywords", keywords_default, key="keywords")

        description_default = df['description'][0] if df is not None and 'description' in df.columns else ""
        description = st.text_area("Empresa: description", description_default, key="description")

        long_description_default = df['long_description'][0] if df is not None and 'long_description' in df.columns else ""
        long_description = st.text_area("Empresa: long_description (de al menos 120 caracteres)", long_description_default, key="long_description")


        # Check form
        if st.form_submit_button("Enviar"):
            errors = False
            # Check passwords
            if password != repeat_password:
                st.error("Las contraseñas no coinciden.")
                errors = True
            
            # Check long description
            if len(long_description) < 120:
                st.error("La descripción larga debe tener al menos 120 caracteres.")
                errors = True
            
            # Check email
            if "@" not in email:
                st.error("El email no es válido.")
                errors = True
            
            # Check empty fields
            if "" in [email, username, name, surname, password, repeat_password, company_name, address, website, phone, cif, country, province, city, postal, keywords, description, long_description]:
                st.error("No puede haber campos vacíos.")
                errors = True
            
            if errors:
                return company_data
            
            # Save in json
            company_data = {
                "email": email,
                "username": username,
                "name": name,
                "surname": surname,
                "password": password,
                "company_name": company_name,
                "address": address,
                "website": website,
                "phone": phone,
                "cif": cif,
                "country": country,
                "province": province,
                "dondeestamos_province": dondeestamos_province,
                "city": city,
                "postal": postal,
                "category_dondeestamos": category_dondeestamos,
                "keywords": keywords,
                "description": description,
                "long_description": long_description
            }

    return company_data


def callback_robot(ret_val: int | None, result_path: str, kwargs_callbacks: dict, run_robot_kwargs: dict):  # pylint: disable=W0613
    """
    If robot fails, have a recovery.
    ret_val: int | None - return code of robot
    result_path: str - path where results are stored
    kwargs_callbacks: dict - kwargs of callbacks
    Arguments in run_robot_kwargs:
        id_: str, 
        vars_: list, 
        robot: str, 
        output_dir: str | None = None, 
        callback: list[Callable[[dict], None]] = [],
        kwargs_callbacks: dict = {},
        msg_file: str | None = None,
        msg_info=None,
        pabot=False, 
        include_tags=[]
    Columns of msg_csv: id_execution, robot (without .robot), status, exception, msg
    """
    kit_digital: KitDigital = kwargs_callbacks["kit_digital"]

    # Get variables
    vars_ = run_robot_kwargs["vars_"]
    id_execution = [x for x in vars_ if "ID_EXECUTION" in x][0].split(":")[1].strip('"')
    msg_csv = [x for x in vars_ if "RETURN_FILE" in x][0].split(":")[1].strip('"')

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        st.warning("No se ha subido a ninguna página.")
        # Send notification
        url: str = kit_digital.url
        pages: list = run_robot_kwargs["include_tags"] 
        kit_digital = send_contact_to_ntfy(kit_digital, f"No ha funcionado la automatización para {url}. Paginas: {str(pages)}.")
        return

    # Check if status is PASS
    info_file = [x for x in vars_ if "INFO_FILE" in x][0].split(":")[1].strip('"')
    with open(info_file, 'r', encoding='utf-8') as f:
        company_data = json.load(f)

    df_pass = df_id[df_id["status"] == "PASS"]
    for row in df_pass.itertuples():
        # Get stage
        robot: str = row.robot
        stage = StageType[robot.upper()]

        # Store company_data, url and screenshot
        kit_digital.stages[stage].info["company_data"] = company_data
        url_screenshot: tuple[str, str] = row.msg.split("|")
        for output in url_screenshot:
            if "URL" in output:
                kit_digital.stages[stage].info["url"] = ":".join(output.split(":")[1:]).strip()
            elif "SCREENSHOT" in output:
                kit_digital.stages[stage].info["screenshot"] = output.split(":")[1].strip()
        
        # Update stage
        kit_digital.stages[stage].status = StageStatus.PASS

        kit_digital.to_yaml()

    # Check if status is RETRY
    df_retry = df_id[df_id["status"] == "FAIL"]
    if len(df_retry) > 0:
        # Set Fail to stages
        for row in df_retry.itertuples():
            # Get stage
            robot: str = row.robot
            stage = StageType[robot.upper()]
        
            # Update stage
            kit_digital.stages[stage].status = StageStatus.FAIL
            kit_digital.stages[stage].info["company_data"] = company_data

            # Get all messages from this robot
            df_robot = df_id[df_id["robot"] == robot]
            msgs = []
            for row in df_robot.itertuples():
                msgs.append(row.msg)
            kit_digital.stages[stage].info["error"] = ", ".join(msgs)
            kit_digital.to_yaml()

        # Show error messages
        for i in range(len(df_retry)):
            if "VariableError" in df_retry["exception"].iloc[i]:
                variable = df_retry["exception"].iloc[i].split("VariableError:")[1].strip()
                msg = df_retry["msg"].iloc[i]
                st.warning(f"Error en la variable {variable}: {msg}")
            else:
                msg = df_retry["msg"].iloc[i]
                st.warning(f"Error: {msg}")

    


def run_robot(kit_digital: KitDigital, info_file: str, results_path: str):
    """
    Run robot that not PASS.
    """
    callupcontact_stage: Stage = kit_digital.stages[StageType.CALLUPCONTACT]
    dondeestamos_stage: Stage = kit_digital.stages[StageType.DONDEESTAMOS]
    travelful_stage: Stage = kit_digital.stages[StageType.TRAVELFUL]

    include_tags = []
    if callupcontact_stage.status != StageStatus.PASS:
        include_tags.append("callupcontact")
        kit_digital.stages[StageType.CALLUPCONTACT].status = StageStatus.PROGRESS
    if dondeestamos_stage.status != StageStatus.PASS:
        include_tags.append("dondeestamos")
        kit_digital.stages[StageType.DONDEESTAMOS].status = StageStatus.PROGRESS
    if travelful_stage.status != StageStatus.PASS:
        include_tags.append("travelful")
        kit_digital.stages[StageType.TRAVELFUL].status = StageStatus.PROGRESS

    kit_digital.to_yaml()


    # Before executing the robot, empty the message file
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    args = [
        f'INFO_FILE:"{info_file}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"'
    ]

    ret_code = asyncio.run(robot_handler.run_robot(
        "directorios", 
        args, 
        "citaciones", 
        output_dir=results_path,
        callbacks=[callback_robot],
        kwargs_callbacks={"kit_digital": kit_digital},
        msg_info=f"Subiendo páginas {' '.join(include_tags)}",
        include_tags=include_tags,
        pabot=True
    ))

    return ret_code


def run_robot_get_provinces(kit_digital: KitDigital, provincia_short: str, results_path: str) -> tuple[KitDigital, list[str]]:    
    # Before executing the robot, empty the message file
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    args = [
        f'province_dondeestamos:"{provincia_short}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"'
    ]

    asyncio.run(robot_handler.run_robot(
        "directorios", 
        args, 
        "citaciones", 
        output_dir=results_path,
        msg_info=f"Obteniendo localidades en {provincia_short}",
        include_tags=['get_localidad'],
        pabot=True
    ))

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        st.warning("No se ha podido obtener las provincias.")
        kit_digital = send_contact_to_ntfy(kit_digital, f"No ha funcionado el get_localidades en {provincia_short}.")
        return kit_digital, []

    # Check if status is PASS
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        # Get msg and parse string list to list
        msg: str = df_id["msg"].iloc[0]
        localidades = msg.replace("[", "").replace("]", "").replace("'", "").split(";")
        localidades = [x.strip() for x in localidades]
        return kit_digital, localidades
    
    # Check if status is FAIL
    df_fail = df_id[df_id["status"] == "FAIL"]
    if len(df_fail) > 0:
        # Get all messages from this robot
        st.warning(f"No se ha podido obtener las provincias de {provincia_short}")
    
    return kit_digital, []


def get_dondeestamos_localidad(kit_digital: KitDigital) -> tuple[KitDigital, str]:
    
    # Make the form
    provinces = [] if not hasattr(st.session_state, "provinces") else st.session_state.provinces
    province_short: str = "" if not hasattr(st.session_state, "province_short") else st.session_state.province_short
    dondeestamos_province = "" if not hasattr(st.session_state, "dondeestamos_province") else st.session_state.dondeestamos_province

    st.markdown("### Obtener la localidad del negocio")
    
    if province_short:
        st.info(f"La provincia es {province_short}")
        if st.button("Cambiar provincia"):
            st.session_state.dondeestamos_province = ""
            st.session_state.province_short = ""
            st.session_state.provinces = []
            st.rerun()

    if dondeestamos_province:
        st.info(f"La localidad del negocio es {dondeestamos_province}")
        if st.button("Cambiar localidad"):
            st.session_state.dondeestamos_province = ""
            st.rerun()
    
    if not provinces:
        st.info("Para la página donde estamos, es necesario obtener la localidad del negocio. Para ello, se obtienen las provincias de la página y se obtienen las localidades de cada provincia.")
        with st.form("Localidades"):
            province_short = st.text_input("Proporciona la provincia para obtener las localidades", value=province_short)
            if st.form_submit_button("Enviar"):
                results_path = kit_digital.stages[StageType.DONDEESTAMOS].results_path
                (kit_digital, provinces) = run_robot_get_provinces(kit_digital, province_short, results_path)
                st.session_state.provinces = provinces
                st.session_state.province_short = province_short
    
    if not hasattr(st.session_state, "provinces") or not st.session_state.provinces:
        st.stop()

    if not dondeestamos_province and provinces:
        with st.form("Localidad dondeestamos"):
            dondeestamos_province = st.selectbox("Selecciona la provincia del negocio.", provinces)
            if st.form_submit_button("Enviar"):
                st.session_state.dondeestamos_province = dondeestamos_province

    if not hasattr(st.session_state, "dondeestamos_province") or not st.session_state.dondeestamos_province:
        st.stop()

    return kit_digital, st.session_state.dondeestamos_province  # type: ignore
    

def directories(kit_digital: KitDigital) -> KitDigital:
    # Create Urls Stage
    directories_stage: Stage = kit_digital.stages[StageType.DIRECTORIES]

    # Necessary files
    company_file = os.path.join(directories_stage.results_path, "company.json")

    # Get provinces for dondeestamos
    kit_digital, dondeestamos_province = get_dondeestamos_localidad(kit_digital)   # type: ignore
    
    # Get variables
    company_data = get_robot_variables(kit_digital, dondeestamos_province)

    # If is data means that the form has been submitted. Run the robot
    if len(company_data) > 0:
        # Save info
        directories_stage.status = StageStatus.PROGRESS
        directories_stage.info["company_data"] = company_data
        kit_digital.stages[StageType.DIRECTORIES] = directories_stage
        kit_digital.to_yaml()

        # Save data in a new company.json
        with open(company_file, 'w', encoding='utf-8') as f:
            json.dump(directories_stage.info["company_data"], f, indent=4)

        # Run robot
        run_robot(kit_digital, company_file, directories_stage.results_path)
        
        # Mark Directories as PASS if all robots are PASS
        travel_pass = kit_digital.stages[StageType.TRAVELFUL].status == StageStatus.PASS
        donde_pass = kit_digital.stages[StageType.DONDEESTAMOS].status == StageStatus.PASS
        callup_pass = kit_digital.stages[StageType.CALLUPCONTACT].status == StageStatus.PASS

        stage = kit_digital.stages[StageType.DIRECTORIES]
        if not (travel_pass and donde_pass and callup_pass):
            st.warning('No se han subido correctamente los datos a los directorios.')
            stage.status = StageStatus.FAIL
            stage.info["error"] = "Fallo robotframework."
            kit_digital.stages[StageType.DIRECTORIES] = stage
            kit_digital.to_yaml()
        else:
            stage.status = StageStatus.PASS
            kit_digital.stages[StageType.DIRECTORIES] = stage
            kit_digital.to_yaml()

    return kit_digital
