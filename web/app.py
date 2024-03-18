from typing import List
import requests
import streamlit as st
import utils.remote_browser as remote_browser
import utils.firebase as firebase
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
from stages.last_touches import add_last_touches
from kitdigital import Directory, KitDigital, Stage, StageStatus, StageType


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

def restart_browser(kit_d: KitDigital) -> KitDigital:
    """
    Restart browser.
    """
    restart = st.button("Reiniciar Navegador", type='primary')
    if restart:
        kit_d = remote_browser.delete_browser_after_stage(kit_d)
        kit_d.to_yaml()
        st.rerun()

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
    # Check if came from stripe
    url_params = st.query_params
    
    if "uid" in url_params and "kdid" in url_params:
        url: str = firebase.check_user_and_kit(url_params["uid"], url_params["kdid"])
        if not url:
            st.error("Algo salió mal. Contacte con nosotros")
            st.stop()
        
        st.session_state.url = url

        # Create directory for results for this url
        kit_d = KitDigital.get_kit_digital(url)

        if not kit_d:
            kit_d = KitDigital(url)
            requests.post(
                "https://notifications.paipaya.com/kit_digital",
                headers={
                    "X-Email": "paipayainfo@gmail.com",
                    "Tags": "white_check_mark"
                },
                data=f"Nuevo Kit: {url}.",
                timeout=15
            )

    else:
        print("No informacion de la url")
        st.error("Permission denied. Access to https://kitdigital.paipaya.com. If problem pressist, contact with us.")
        requests.post(
                "https://notifications.paipaya.com/kit_digital_fail",
                headers={
                    "X-Email": "paipayainfo@gmail.com"
                },
                data=f"Se ha intentado acceder directamente sin query params.",
                timeout=15
            )
        st.stop()
    
    if kit_d is None or not isinstance(kit_d, KitDigital):    
        st.error("No se ha podido crear el kit digital.")
        st.stop()
        raise Exception("No se ha podido crear el kit digital.")
    
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
    initial_sidebar_state="collapsed"
)

# Initialize firebase
firebase.inicialize_app()


# with st.sidebar:
#     logo_path = st.secrets["paths"]["logo_path"]
#     st.image(logo_path)
#     st.write("Paipaya © 2023")
#     with st.expander("Contacto", expanded=False):
#         st.markdown("# Soluciones con inteligencia artificial")
#         st.markdown("Contacte con nosotros: d.correas.oliver@gmail.com")

title_placeholder = st.empty()
title_placeholder.markdown("# Kit Digital")

st.markdown("---")

# Create Kit Digital
created_kit_digital: KitDigital | None = None
created_kit_digital = get_create_kit_digital()

assert created_kit_digital is not None, "No se ha podido crear el kit digital."
kit_digital: KitDigital = created_kit_digital

title_placeholder.markdown(f"# Kit Digital ({kit_digital.url})")

val = stx.stepper_bar(steps=[
    "Aceptar cookies", 
    "Seleccionar Urls", 
    "Subir Directorios", 
    "Seo Básico", 
    "Obtener H1, H2, H3", 
    "Obtener el logo de Kit Digital", 
    "Pantallazos Urls", 
    "Pantallazos Multiidioma",
    "Últimos ajustes",
    "Resultados"
    ],
    lock_sequence=False
)

# Crawl urls
if val == 0:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/gjMS0kFQwyw")

    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Aceptar cookies", kit_digital.stages[StageType.ACCEPT_COOKIES].status)
    with col2:
        restart_stage(kit_digital, StageType.ACCEPT_COOKIES)
        restart_browser(kit_digital)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es aceptar las cookies para que no aparezcan los popups de cookies en los pantallazos.')
    
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status != StageStatus.PASS:
        kit_digital = accept_cookies(kit_digital)
        if kit_digital.stages[StageType.ACCEPT_COOKIES].status == StageStatus.PASS:
            st.rerun()
    
    # Show cookies
    if kit_digital.stages[StageType.ACCEPT_COOKIES].status == StageStatus.PASS:
        st.markdown("### Se han aceptado las cookies por un usuario.")

if val == 1:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/nrlNjY8jmp0")

    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener urls y seleccionar las válidas", kit_digital.stages[StageType.SELECT_URLS].status)
    with col2:
        restart_stage(kit_digital, StageType.CRAWL_URLS, optional_stages=[StageType.SELECT_URLS])

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es obtener las urls de la página y seleccionar las urls a las que se harán pantallazos. Deben de estar las urls que representen el menú de opciones de la página creada (home, contactos, blog, etc.).')

    if kit_digital.stages[StageType.CRAWL_URLS].status != StageStatus.PASS:
        kit_digital = crawl_urls(kit_digital)
        if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show suggested urls
    if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
        urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
        st.markdown("### Urls sugeridas")
        st.write(urls_stage.info["suggested_urls"])

        if "suggested_urls_multi" in urls_stage.info:
            st.markdown("### Urls sugeridas multi-idioma")
            st.write(urls_stage.info["suggested_urls_multi"])

    # Select urls
    st.markdown("### Seleccion de urls")
    if kit_digital.stages[StageType.SELECT_URLS].status != StageStatus.PASS:
        kit_digital = select_urls(kit_digital)
        if kit_digital.stages[StageType.SELECT_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show urls
    if kit_digital.stages[StageType.SELECT_URLS].status == StageStatus.PASS:
        urls_stage: Stage = kit_digital.stages[StageType.SELECT_URLS]
        st.markdown("### Urls seleccionadas")
        st.write(urls_stage.info["urls"])

        if "urls_multi" in urls_stage.info:
            st.markdown("### Urls seleccionadas multi-idioma")
            st.write(urls_stage.info["urls_multi"])

if val == 2:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/p5J038qah08")
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Subir directorios", kit_digital.stages[StageType.DIRECTORIES].status)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es posicionar la página en la web. Para ello, se sube la información del cliente y la url de la página en 3 directorios.')

    if not "directories" in kit_digital.stages[StageType.DIRECTORIES].info:
        kit_digital.stages[StageType.DIRECTORIES].info["directories"] = []
    kit_digital = support_legacy_directories(kit_digital)
    
    # Show directories
    directories_: List[Directory] = kit_digital.stages[StageType.DIRECTORIES].info.get("directories", [])
    faltan_text = "" if len(directories_) >= 3 else f"(faltan {3 - len(directories_)} directorios)"
    
    st.markdown(f"## Se han subido <span style='color:green'>{len(directories_)}</span> directorios <span style='color:red'>{faltan_text}</span>", unsafe_allow_html=True)
    if len(directories_) < 3:
        st.info("Se pueden añadir directorios manualmente o subirlos automáticamente.")
    for directory in directories_:
        with st.expander(f"{directory['name']}"):
            st.markdown(f"### {directory['name']}")
            st.markdown(f"URL: {directory['url']}")
            st.image(directory["screenshot"])
    
    st.markdown("## Añadir directorio manualmente")
    with st.expander("Añadir directorio manualmente", expanded=True):
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

if val == 3:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/kPlPjTpIfdM")
    # SEO Basico
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("SEO Básico", kit_digital.stages[StageType.SEO_BASICO].status)
    with col2:
        restart_stage(kit_digital, StageType.SEO_BASICO)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es redactar el texto con el que se justificará que se ha hecho un posicionamiento SEO en la página.')

    if kit_digital.stages[StageType.SEO_BASICO].status != StageStatus.PASS:
        kit_digital = set_seo_basico(kit_digital)
        if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
            st.rerun()

    # Show SEO Basico
    if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
        kit_digital = show_modiffy_results(kit_digital)

if val == 4:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/WgRdCuCTwoc")
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
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/ZOWwZux76oA")
    # Acreditacion cumplimiento en materia de publicidad
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Obtener el logo de Kit Digital", kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status)
    with col2:
        restart_stage(kit_digital, StageType.LOGO_KIT_DIGITAL)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es hacer un pantallazo sobre el logo del kit digital y la unión europea dentro de la página. Es recomendable señalar en un recuadro el logo, por lo que es necesario marcarlo con el ratón y después guardarlo.')

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
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/xV6sh1NdnkU")
    # Plantilla de recopilacion de evidencias
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Plantilla de recopilación de evidencias 1: Pantallazos", kit_digital.stages[StageType.PANTALLAZOS_URLS].status)
    with col2:
        restart_stage(kit_digital, StageType.PANTALLAZOS_URLS)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es hacer un pantallazo de las urls seleccionadas.')

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
        get_pantallazos_urls(
            kit_digital,
            urls=kit_digital.stages[StageType.SELECT_URLS].info["urls"],
            stage=StageType.PANTALLAZOS_URLS,
            capture_mobile=True
        )
        if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
            st.rerun()

    # Show screenshots
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
        st.success("Estos son los pantallazos obtenidos.")
        for i, screenshot_path in enumerate(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["screenshots"]):
            with st.expander(f"Pantallazo {i+1}"):
                st.image(screenshot_path)
        # Show mobile, desktop and ipad screenshots
        with st.expander("Pantallazos móvil"):
            st.image(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["mobile_screenshot"])
        with st.expander("Pantallazos ipad"):
            st.image(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["ipad_screenshot"])
        with st.expander("Pantallazos escritorio"):
            st.image(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["desktop_screenshot"])
        

if val == 7:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/QsELXW1BVuc")
    # Plantilla de recopilacion de evidencias multi-idioma
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Plantilla de recopilación de evidencias 2: Pantallazos multi-idioma", kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status)
    with col2:
        restart_stage(kit_digital, StageType.PANTALLAZOS_MULTIIDIOMA)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es hacer un pantallazo de las urls seleccionadas en multi-idioma. Se debe de cambiar el idioma manualmente en el navegador.')

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
        if not "urls_multi" in kit_digital.stages[StageType.SELECT_URLS].info:
            st.warning("Para que se realicen los pantallazos automáticamente, se deben de seleccionar las urls multi-idioma en el paso 2. " +
                       "Si la página no tiene urls multi-idioma, se puede realizar los pantallazos con las siguientes instrucciones.")
            st.info("Para realizar los pantallazos sigue las siguientes instrucciones: \n" +
                    "1. En el navegador que se abre, se abrirán los enlaces a las páginas que hay que hacer pantallazo. \n" +
                    "2. Espere el mensaje verde debajo del navegador indicando que ya ha terminado de abrir el navegador. \n" +
                    "3. Dentro del navegador, cambia la página de idioma. \n" +
                    "4. Una vez se haya cambiado la página, click en el botón de abajo donde pone 'Realizar pantallazo'. \n" +
                    "5. Espere a que se haga el pantallazo y vuelve a esperar por el paso 1. \n"
                )
            get_pantallazos_multiidioma(kit_digital)
        else:
            get_pantallazos_urls(
                kit_digital,
                urls=kit_digital.stages[StageType.SELECT_URLS].info["urls_multi"],
                stage=StageType.PANTALLAZOS_MULTIIDIOMA,
                capture_mobile=False
            )
        if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
            st.rerun()

    # Show Plantilla de recopilacion de evidencias multi-idioma
    if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == StageStatus.PASS:
        st.success("Estos son los pantallazos obtenidos.")
        for i, screenshot_path in enumerate(kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["screenshots"]):
            with st.expander(f"Pantallazo {i+1}"):
                st.image(screenshot_path)
            

if val == 8:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/D8GAIhZgl2g")
    col1, col2 = st.columns([4, 1])
    with col1:
        display_title("Últimos ajustes", kit_digital.stages[StageType.LAST_TOUCHES].status)
    with col2:
        restart_stage(kit_digital, StageType.LAST_TOUCHES)

    # st.sidebar.markdown("# Información del paso")
    # st.sidebar.success('El objetivo de este paso es completar información que faltaría para tener todo subido en la plataforma.')

    if kit_digital.stages[StageType.LAST_TOUCHES].status != StageStatus.PASS:
        rerun_later = True
    else:
        rerun_later = False
    
    kit_digital: KitDigital = add_last_touches(kit_digital)
    
    if rerun_later and kit_digital.stages[StageType.LAST_TOUCHES].status == StageStatus.PASS:
        st.rerun()


# If all stages pass, delete browser
stages_no_directories = {
    stage_type: stage for stage_type, stage in kit_digital.stages.items() if stage_type != StageType.CALLUPCONTACT and \
        stage_type != StageType.DONDEESTAMOS and \
        stage_type != StageType.TRAVELFUL
}
if all([x.status == StageStatus.PASS for x in stages_no_directories.values()]):
    kit_digital = remote_browser.delete_browser_after_stage(kit_digital)
    kit_digital.to_yaml()
    status_result = StageStatus.PASS
else:
    status_result = StageStatus.PENDING 


if val == 9:
    with st.expander("Tutorial en vídeo", expanded=False):
        st.video("https://youtu.be/i87T5O5dG3I")
    display_title("Resultados",status_result)
    show_results(kit_digital)
