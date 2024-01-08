from typing import List
import requests
import streamlit as st
import utils.remote_browser as remote_browser
import extra_streamlit_components as stx
from stages.accept_cookies import accept_cookies
from stages.directories import directories, add_directory_manually, support_legacy_directories
from stages.crawl_urls import crawl_urls, select_urls
from stages.seo_basico import set_seo_basico, show_modiffy_results
from stages.headers import get_headers
from stages.logo_kit import get_logo_kit
from stages.pantallazos_urls import get_pantallazos_urls
from stages.pantallazos_multiidioma import get_pantallazos_multiidioma
from stages.results import show_results
from kitdigital import Directory, KitDigital, Stage, StageStatus, StageType
import streamlit as st
from utils.google_auth import Google_auth


# Probar con: https://djadelpeluqueria.es/

def restart_stage(kit_d: KitDigital, stage_type: StageType, optional_stages: list[StageType] | None =None) -> KitDigital:
    """
    Restart a stage.
    """
    if optional_stages is None:
        optional_stages = []

    restart = st.button("Reiniciar Paso", type='primary')
    if restart:
        st.session_state["executing_cookies"] = False
        st.session_state["executing_screenshots"] = False
        st.session_state["executing_logo"] = False

        stage: Stage = kit_d.stages[stage_type]
        stage.status = StageStatus.PENDING
        stage.info = {}
        kit_d.stages[stage_type] = stage
        for stage_type in optional_stages:
            stage: Stage = kit_d.stages[stage_type]
            stage.status = StageStatus.PENDING
            stage.info = {}
            kit_d.stages[stage_type] = stage
        kit_d.to_yaml()
    return kit_d

def get_create_kit_digital() -> KitDigital:
    """
    Get or create a KitDigital object from yaml.
    """
    if hasattr(st.session_state, "url") and st.session_state.url:
        url = st.session_state.url
        kit_d = KitDigital.get_kit_digital(url)
        if kit_d:
            return kit_d
    
    kit_d = None
    placeholder = st.empty()
    with placeholder.form("Obtener urls"):
        st.info("La url debe ser la página principal del dominio. Debe contener el prefijo http o https.")
        st.write("Proporciona la url del dominio")
        url = st.text_input("URL")

        if st.form_submit_button("Enviar"):
            # Check if url is valid
            if not url.startswith("http"):
                st.error("La url debe empezar por http o https.")
                st.stop()

            st.session_state.url = url
            # Create directory for results for this url
            kit_d = KitDigital.get_kit_digital(url)

            if not kit_d:
                kit_d = KitDigital(url, st.session_state["login"])
                requests.post(
                    "https://notifications.paipaya.com/kit_digital",
                    headers={
                        "X-Email": "paipayainfo@gmail.com",
                        "Tags": "white_check_mark"
                    },
                    data=f"Nuevo Kit: {url}.",
                    timeout=15
                )

    if not kit_d:
        st.stop()
    else:
        placeholder.empty()
    
    assert kit_d is not None, "No se ha podido crear el kit digital."
    return kit_d

def display_title(msg: str, status: StageStatus):
    """
    Display title.
    """
    if status == StageStatus.PASS:
        status_msg = '✅ <span style="color:green">Completado:</span>'
    elif status == StageStatus.FAIL:
        status_msg = '❌ <span style="color:red">Fallo:</span>'
    elif status == StageStatus.PENDING:
        status_msg = '🕒 <span style="color:blue">Pendiente:</span>'
    elif status == StageStatus.PROGRESS:
        status_msg = '🕒 <span style="color:orange">En progreso:</span>'
    elif status == StageStatus.SKIP:
        status_msg = '👷 <span style="color:grey">No disponible:</span>'
    else:
        status_msg = ""

    st.markdown(f'# {status_msg} {msg}', unsafe_allow_html=True)

st.set_page_config(
    page_title="Kit Digital",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded"
)


with st.sidebar:
    logo_path = st.secrets["paths"]["logo_path"]
    st.image(logo_path)
    st.write("Paipaya © 2023")
    with st.expander("Contacto", expanded=False):
        st.markdown("# Soluciones con inteligencia artificial")
        st.markdown("Contacte con nosotros: d.correas.oliver@gmail.com")


### AÑADIR LOGIN
if not st.session_state.get("login", None):
    client_id = "947045396186-n9lpd4b1kl8h8hp0h2vgv2pkdq9pta4o.apps.googleusercontent.com"
    client_secret = "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"
    redirect_uri = "http://localhost:8503"


    user_profile: dict | None = Google_auth(
            clientId=client_id, clientSecret=client_secret, redirect_uri=redirect_uri
        )

    if not user_profile:
        st.stop()
    
    st.session_state["login"] = user_profile.get("email").split("@")[0].upper()


st.write("Has iniciado sesión como", st.session_state["login"])
title_placeholder = st.empty()
title_placeholder.markdown("# Kit Digital (Beta)")

st.markdown("---")

# Create Kit Digital
created_kit_digital: KitDigital | None = None
created_kit_digital = get_create_kit_digital()

assert created_kit_digital is not None, "No se ha podido crear el kit digital."
kit_digital: KitDigital = created_kit_digital

title_placeholder.markdown(f"# Kit Digital (Beta) ({kit_digital.url})")

val = stx.stepper_bar(steps=[
    "Aceptar cookies", 
    "Seleccionar Urls", 
    "Subir Directorios", 
    "Seo Básico", 
    "Obtener H1, H2, H3", 
    "Obtener el logo de Kit Digital", 
    "Pantallazos Urls", 
    "Pantallazos Multiidioma",
    "Informe de accesibilidad",
    "Resultados"
    ],
    lock_sequence=False
)

# Crawl urls
if val == 0:
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Aceptar cookies", kit_digital.stages[StageType.ACCEPT_COOKIES].status)
    with col2:
        restart_stage(kit_digital, StageType.ACCEPT_COOKIES)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es aceptar las cookies para que no aparezcan los popups de cookies en los pantallazos.')
    
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status != StageStatus.PASS:
        kit_digital = accept_cookies(kit_digital)
        if kit_digital.stages[StageType.ACCEPT_COOKIES].status == StageStatus.PASS:
            st.rerun()
    
    # Show cookies
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status == StageStatus.PASS:
        st.markdown("### Se han aceptado las cookies por un usuario.")

if val == 1:
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener urls y seleccionar las válidas", kit_digital.stages[StageType.SELECT_URLS].status)
    with col2:
        restart_stage(kit_digital, StageType.CRAWL_URLS, optional_stages=[StageType.SELECT_URLS])

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es obtener las urls de la página y seleccionar las urls a las que se harán pantallazos. Deben de estar las urls que representen el menú de opciones de la página creada (home, contactos, blog, etc.).')

    if kit_digital.stages[StageType.CRAWL_URLS].status != StageStatus.PASS:
        kit_digital = crawl_urls(kit_digital)
        if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show suggested urls
    if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
        urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
        st.write(urls_stage.info["suggested_urls"])

    # Select urls
    st.markdown("## Seleccion de urls")
    if kit_digital.stages[StageType.SELECT_URLS].status != StageStatus.PASS:
        kit_digital = select_urls(kit_digital)
        if kit_digital.stages[StageType.SELECT_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show urls
    if kit_digital.stages[StageType.SELECT_URLS].status == StageStatus.PASS:
        urls_stage: Stage = kit_digital.stages[StageType.SELECT_URLS]
        st.write(urls_stage.info["urls"])

if val == 2:
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Subir directorios", kit_digital.stages[StageType.DIRECTORIES].status)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es posicionar la página en la web. Para ello, se sube la información del cliente y la url de la página en 3 directorios.')

    if not "directories" in kit_digital.stages[StageType.DIRECTORIES].info:
        kit_digital.stages[StageType.DIRECTORIES].info["directories"] = []
    kit_digital = support_legacy_directories(kit_digital)
    st.markdown("## Añadir directorio manualmente")
    with st.expander("Añadir directorio manualmente", expanded=False):
        kit_digital = add_directory_manually(kit_digital)
    # Directories
    if kit_digital.stages[StageType.CALLUPCONTACT].status != StageStatus.PASS or \
        kit_digital.stages[StageType.DONDEESTAMOS].status != StageStatus.PASS or \
        kit_digital.stages[StageType.TRAVELFUL].status != StageStatus.PASS:
        kit_digital = directories(kit_digital)
        if kit_digital.stages[StageType.CALLUPCONTACT].status == StageStatus.PASS and \
            kit_digital.stages[StageType.DONDEESTAMOS].status == StageStatus.PASS and \
            kit_digital.stages[StageType.TRAVELFUL].status == StageStatus.PASS:
            st.rerun()

    # Show directories
    directories_: List[Directory] = kit_digital.stages[StageType.DIRECTORIES].info.get("directories", [])
    for directory in directories_:
        with st.expander(f"{directory['name']}"):
            st.markdown(f"### {directory['name']}")
            st.markdown(f"URL: {directory['url']}")
            st.image(directory["screenshot"])

if val == 3:
    # SEO Basico
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("SEO Básico", kit_digital.stages[StageType.SEO_BASICO].status)
    with col2:
        restart_stage(kit_digital, StageType.SEO_BASICO)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es redactar el texto con el que se justificará que se ha hecho un posicionamiento SEO en la página.')

    if kit_digital.stages[StageType.SEO_BASICO].status != StageStatus.PASS:
        kit_digital = set_seo_basico(kit_digital)
        if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
            st.rerun()

    # Show SEO Basico
    if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
        kit_digital = show_modiffy_results(kit_digital)

if val == 4:
    # Headers SEO
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener H1, H2, H3", kit_digital.stages[StageType.HEADERS_SEO].status)
    with col2:
        restart_stage(kit_digital, StageType.HEADERS_SEO)
    if kit_digital.stages[StageType.HEADERS_SEO].status != StageStatus.PASS:
        get_headers(kit_digital)
        if kit_digital.stages[StageType.HEADERS_SEO].status == StageStatus.PASS:
            st.rerun()

    # Show Headers SEO
    if kit_digital.stages[StageType.HEADERS_SEO].status == StageStatus.PASS:
        stage_info = kit_digital.stages[StageType.HEADERS_SEO].info
        h1, h2, h3 = stage_info["suggested_h1"], stage_info["suggested_h2"], stage_info["suggested_h3"]
        for title, header in zip(["H1", "H2", "H3"], [h1, h2, h3]):
            st.markdown(f"### {title}")
            for h in header:
                st.write(h)

if val == 5:
    # Acreditacion cumplimiento en materia de publicidad
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener el logo de Kit Digital", kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status)
    with col2:
        restart_stage(kit_digital, StageType.LOGO_KIT_DIGITAL)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es hacer un pantallazo sobre el logo del kit digital y la unión europea dentro de la página. Es recomendable señalar en un recuadro el logo, por lo que es necesario marcarlo con el ratón y después guardarlo.')

    if kit_digital.stages[StageType.ACCEPT_COOKIES].status != StageStatus.PASS:
        st.warning("Complete el paso 1 (aceptar las cookies) antes de continuar. Sirve para que no aparezcan los popups de cookies en los pantallazos.")
        st.stop()

    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status != StageStatus.PASS:
        get_logo_kit(kit_digital)
        if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == StageStatus.PASS:
            st.rerun()

    # Show Acreditacion cumplimiento en materia de publicidad
    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == StageStatus.PASS:
        st.markdown('### Descargar imagen')
        col1, col2, _ = st.columns([1, 2, 1])
        col2.image(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"])
        with open(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"], "rb") as f:
            col1.download_button(
                label="Descargar imagen",
                data=f,
                file_name="pantallazo_logo.png",
                mime="image/png",
            )
        st.markdown('### Descargar documento pdf')
        with open(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["pdf"], "rb") as f:
            st.download_button(
                label="Descargar documento",
                data=f,
                file_name="pantallazo_logo.pdf",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

if val == 6:
    # Plantilla de recopilacion de evidencias
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Plantilla de recopilación de evidencias 1: Pantallazos", kit_digital.stages[StageType.PANTALLAZOS_URLS].status)
    with col2:
        restart_stage(kit_digital, StageType.PANTALLAZOS_URLS)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es hacer un pantallazo de las urls seleccionadas.')

    stop = False
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status != StageStatus.PASS:
        st.warning("Complete el paso 1 (aceptar las cookies) antes de continuar. Sirve para que no aparezcan los popups de cookies en los pantallazos.")
        stop = True
    if kit_digital.stages[StageType.SELECT_URLS].status != StageStatus.PASS:
        st.warning("Complete el paso 2 (seleccionar urls) antes de continuar.")
        stop = True
    if stop:
        st.stop()
    
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status != StageStatus.PASS:
        get_pantallazos_urls(kit_digital)
        if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show Plantilla de recopilacion de evidencias
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
        st.info("Se puede descargar para visualizar el documento, pero no está terminado. Espere a llegar al apartado de resultados.")
        with open(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["word"], "rb") as f:
            st.download_button(
                label="Descargar documento NO TERMINADO",
                data=f,
                file_name="pantallazos_urls_preview.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="pantallazos_urls"
            )

if val == 7:
    # Plantilla de recopilacion de evidencias multi-idioma
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Plantilla de recopilación de evidencias 2: Pantallazos multi-idioma", kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status)
    with col2:
        restart_stage(kit_digital, StageType.PANTALLAZOS_MULTIIDIOMA)

    st.sidebar.markdown("# Información del paso")
    st.sidebar.success('El objetivo de este paso es hacer un pantallazo de las urls seleccionadas en multi-idioma. Se debe de cambiar el idioma manualmente en el navegador.')

    stop = False
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status != StageStatus.PASS:
        st.warning("Complete el paso 1 (aceptar las cookies) antes de continuar. Sirve para que no aparezcan los popups de cookies en los pantallazos.")
        stop = True
    if kit_digital.stages[StageType.SELECT_URLS].status != StageStatus.PASS:
        st.warning("Complete el paso 2 (seleccionar urls) antes de continuar.")
        stop = True
    if stop:
        st.stop()
    
    if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status != StageStatus.PASS:
        get_pantallazos_multiidioma(kit_digital)
        if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
            st.rerun()

    # Show Plantilla de recopilacion de evidencias multi-idioma
    if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
        st.info("Se puede descargar para visualizar el documento, pero no está terminado. Espere a llegar al apartado de resultados.")
        with open(kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["word"], "rb") as f:
            st.download_button(
                label="Descargar documento NO TERMINADO",
                data=f,
                file_name="pantallazos_multiidioma_preview.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="pantallazos_multiidioma"
            )

if val == 8:
    display_title("Informe de accesibilidad", StageStatus.SKIP)
    st.warning('Se está elaborando el informe de accesibilidad. Aún no está disponible. Plantilla en resultados.')


# If all stages pass, delete browser
if all([x.status == StageStatus.PASS for x in kit_digital.stages.values()]):
    kit_digital = remote_browser.delete_browser_after_stage(kit_digital)
    kit_digital.to_yaml()
    status_result = StageStatus.PASS
else:
    status_result = StageStatus.PENDING 


if val == 9:
    display_title("Resultados",status_result)
    show_results(kit_digital)
