import asyncio
from calendar import c
import os
import requests
import streamlit as st
import utils.robot_handler as robot_handler
from kitdigital import KitDigital, Stage, StageStatus, StageType


def get_create_kit_digital() -> KitDigital | None:
    kit_digital = None

    with st.form("memoria_tecnica"):
        st.write("Proporciona la url del dominio")
        url = st.text_input("URL")

        if st.form_submit_button("Enviar"):

            # Create directory for results for this url
            kit_digital = KitDigital.get_kit_digital(url)
            
            new_kit = True
            if kit_digital:
                st.info("Ya existe un kit digital para esta url.")
                for stage in kit_digital.stages.values():
                    if stage.status == StageStatus.PASS:
                        st.info(f"Ya se ha realizado la etapa {stage.name}.")

                col1, col2 = st.columns(2)
                if col1.button("Borrarlo y crear nueva justificacion", type='secondary'):
                    new_kit = True
                if col2.button("Continuar con el existente"):
                    new_kit = False
                
            if new_kit:
                kit_digital = KitDigital(url)
    
    return kit_digital


def crawl_urls(kit_digital: KitDigital) -> KitDigital:
    # Create Urls Stage
    urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
    urls_stage.status = StageStatus.PROGRESS
    
    output_file = os.path.join(urls_stage.results_path, 'urls.txt')
    args = [
        f'URL:"{kit_digital.url}"',
        f'OUTPUT_FILE:"{output_file}"'
    ]

    ret_code = asyncio.run(robot_handler.run_robot(
        "paginas", 
        args, 
        "KitD_Paginas.robot", 
        output_dir=urls_stage.results_path,
        msg_info=f"Obteniendo páginas",
        msg_fail=f"No se ha obtenido el listado de páginas. Nos pondremos en contacto con usted para solucionar el problema.",
        msg_success=f"Se han obtenido las páginas correctamente"
    ))

    # Falla el crawling
    if ret_code != 0:
        urls_stage.status = StageStatus.FAIL
        urls_stage.info = "Fallo robotframework."

        # Save fail kit_digital
        kit_digital.stages[StageType.CRAWL_URLS] = urls_stage

        with st.form("Contacto"):
            st.write("Proporciona tu email para que nos pongamos en contacto contigo")
            email = st.text_input("Email")

            if st.form_submit_button("Enviar"):
                
                # Save info
                urls_stage.info += f" Email: {email}"
                kit_digital.stages[StageType.CRAWL_URLS] = urls_stage
                
                # Send notification
                requests.post(
                    "https://notifications.paipaya.com/kit_digital_fail",
                    headers={
                        "X-Email": "paipayainfo@gmail.com",
                        "Tags": "warning"
                    },
                    data=f"El robot de obtención de páginas ha fallado en la url {kit_digital.url}. El email del usuario es {email}."
        )
    
    # Tiene exito el crawling
    else:
        urls_stage.status = StageStatus.PASS

        # Save success kit_digital
        kit_digital.stages[StageType.CRAWL_URLS] = urls_stage
        kit_digital.to_yaml()

    return kit_digital




with st.sidebar:
    logo_path = st.secrets["paths"]["logo_path"]
    st.image(logo_path)
    st.write("Paipaya © 2023")

st.markdown("# Kit Digital")

st.markdown("---")

st.markdown("## Datos para la elaboración de la justificación.")


# Create Kit Digital
created_kit_digital: KitDigital | None = None
if not hasattr(st.session_state, "kit_digital"):
    created_kit_digital = get_create_kit_digital()
    if created_kit_digital:
        st.session_state.kit_digital = created_kit_digital
else:
    created_kit_digital = st.session_state.kit_digital

if not created_kit_digital:
    st.stop()

assert created_kit_digital is not None, "No se ha podido crear el kit digital."
kit_digital: KitDigital = created_kit_digital


# Crawl urls
if kit_digital.stages[StageType.CRAWL_URLS].status != StageStatus.PASS:
    kit_digital = crawl_urls(kit_digital)
    kit_digital.to_yaml()

# Show urls
if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
    urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
    urls_file = os.path.join(urls_stage.results_path, "urls.txt")
    with open(urls_file, 'r') as f:
        urls = f.read().splitlines()
        st.write(urls)


