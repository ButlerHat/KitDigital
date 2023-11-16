import streamlit as st
import utils.get_browser as get_browser
import extra_streamlit_components as stx
from stages.accept_cookies import accept_cookies
from stages.directories import directories
from stages.crawl_urls import crawl_urls, select_urls
from stages.seo_basico import set_seo_basico
from stages.headers import get_headers
from stages.logo_kit import get_logo_kit
from stages.pantallazos_urls import get_pantallazos_urls
from stages.pantallazos_multiidioma import get_pantallazos_multiidioma
from kitdigital import KitDigital, Stage, StageStatus, StageType


# Probar con: https://djadelpeluqueria.es/

def restart_stage(kit_d: KitDigital, stage_type: StageType, optional_stages: list[StageType] | None =None) -> KitDigital:
    """
    Restart a stage.
    """
    if optional_stages is None:
        optional_stages = []

    restart = st.button("Reiniciar Stage", type='primary')
    if restart or st.session_state.get(f'ask_{stage_type}', False):
        if f'ask_{stage_type}' not in st.session_state:
            st.session_state[f'ask_{stage_type}'] = True
        if restart:
            st.session_state[f'ask_{stage_type}'] = True
        st.warning("¿Estás seguro de que quieres reiniciar esta etapa? Se perderán los datos que hayas introducido.")
        yes_button = st.button("Sí, reiniciar etapa", type='primary')
        no_button = st.button("No, no reiniciar etapa")
        if yes_button:
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
            st.session_state[f'ask_{stage_type}'] = False
        elif no_button:
            st.session_state[f'ask_{stage_type}'] = False

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
    with st.form("Obtener urls"):
        st.info("La url debe ser la página principal del dominio. Desde esta se navegaran a las demás páginas y se obtendran cabeceras, etc.")
        st.write("Proporciona la url del dominio")
        url = st.text_input("URL")

        if st.form_submit_button("Enviar"):
            st.session_state.url = url
            # Create directory for results for this url
            kit_d = KitDigital.get_kit_digital(url)

            if not kit_d:
                kit_d = KitDigital(url)

    if not kit_d:
        st.stop()
    
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
    st.markdown("# Soluciones con inteligencia artificial")
    st.markdown("Contacte con nosotros: d.correas.oliver@gmail.com")

title_placeholder = st.empty()
title_placeholder.markdown("# Kit Digital (Beta)")

st.markdown("---")

# Create Kit Digital
created_kit_digital: KitDigital | None = None
created_kit_digital = get_create_kit_digital()

assert created_kit_digital is not None, "No se ha podido crear el kit digital."
kit_digital: KitDigital = created_kit_digital

title_placeholder.markdown(f"# Kit Digital (Beta) ({kit_digital.url})")

val = stx.stepper_bar(steps=["Aceptar cookies", "Seleccionar Urls", "Subir Directorios", "Seo Básico", "Obtener H1, H2, H3", "Obtener el logo de Kit Digital", "Pantallazos Urls", "Pantallazos Multiidioma"])

# Crawl urls
if val == 0:
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Aceptar cookies", kit_digital.stages[StageType.ACCEPT_COOKIES].status)
    with col2:
        restart_stage(kit_digital, StageType.ACCEPT_COOKIES)
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
    # Directories
    if kit_digital.stages[StageType.DIRECTORIES].status != StageStatus.PASS:
        kit_digital = directories(kit_digital)
        if kit_digital.stages[StageType.DIRECTORIES].status == StageStatus.PASS:
            st.rerun()

    # Show directories
    if kit_digital.stages[StageType.DIRECTORIES].status == StageStatus.PASS:
        st.markdown("### Callupcontact")
        with st.expander("Evidencia Callupcontact", expanded=False):
            st.image(kit_digital.stages[StageType.CALLUPCONTACT].info["screenshot"])
        
        st.markdown("### Donde estamos")
        with st.expander("Evidencia Donde estamos", expanded=False):
            st.image(kit_digital.stages[StageType.DONDEESTAMOS].info["screenshot"])
        
        st.markdown("### Travelful")
        with st.expander("Evidencia Travelful", expanded=False):
            st.image(kit_digital.stages[StageType.TRAVELFUL].info["screenshot"])

if val == 3:
    # SEO Basico
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("SEO Básico", kit_digital.stages[StageType.SEO_BASICO].status)
    with col2:
        restart_stage(kit_digital, StageType.SEO_BASICO)
    if kit_digital.stages[StageType.SEO_BASICO].status != StageStatus.PASS:
        kit_digital = set_seo_basico(kit_digital)
        if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
            st.rerun()

    # Show SEO Basico
    if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
        st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["text_before_headers"])
        st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["text_after_headers"])
        st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["multiidioma"])

if val == 4:
    # Headers SEO
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener H1, H2, H3", kit_digital.stages[StageType.HEADERS_SEO].status)
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

    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status != StageStatus.PASS:
        get_logo_kit(kit_digital)
        if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == StageStatus.PASS:
            st.rerun()

    # Show Acreditacion cumplimiento en materia de publicidad
    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == StageStatus.PASS:
        st.image(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"])
        with open(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["word"], "rb") as f:
            st.download_button(
                label="Descargar documento",
                data=f,
                file_name="pantallazo_logo.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if val == 6:
    # Plantilla de recopilacion de evidencias
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Plantilla de recopilación de evidencias 1: Pantallazos", kit_digital.stages[StageType.PANTALLAZOS_URLS].status)
    with col2:
        restart_stage(kit_digital, StageType.PANTALLAZOS_URLS)

    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status != StageStatus.PASS:
        get_pantallazos_urls(kit_digital)
        if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show Plantilla de recopilacion de evidencias
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
        with open(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["word"], "rb") as f:
            st.download_button(
                label="Descargar documento",
                data=f,
                file_name="pantallazos_urls.docx",
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
    
    if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status != StageStatus.PASS:
        get_pantallazos_multiidioma(kit_digital)
        if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
            st.rerun()

    # Show Plantilla de recopilacion de evidencias multi-idioma
    if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
        with open(kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["word"], "rb") as f:
            st.download_button(
                label="Descargar documento",
                data=f,
                file_name="pantallazos_multiidioma.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="pantallazos_multiidioma"
            )

# If all stages pass, delete browser
if all([x.status == StageStatus.PASS for x in kit_digital.stages.values()]):
    kit_digital = get_browser.delete_browser_after_stage(kit_digital)
    kit_digital.to_yaml()



