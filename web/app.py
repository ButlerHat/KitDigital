import streamlit as st
from stages.directories import directories
from stages.crawl_urls import crawl_urls, select_urls
from stages.seo_basico import set_seo_basico
from stages.headers import get_headers
from stages.logo_kit import get_logo_kit
from stages.pantallazos_urls import get_pantallazos_urls
from kitdigital import KitDigital, Stage, StageStatus, StageType


# Probar con: https://djadelpeluqueria.es/

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


with st.sidebar:
    logo_path = st.secrets["paths"]["logo_path"]
    st.image(logo_path)
    st.write("Paipaya © 2023")

st.markdown("# Kit Digital")

st.markdown("---")

st.markdown("## Datos para la elaboración de la justificación.")


# Create Kit Digital
created_kit_digital: KitDigital | None = None
created_kit_digital = get_create_kit_digital()

assert created_kit_digital is not None, "No se ha podido crear el kit digital."
kit_digital: KitDigital = created_kit_digital

# Crawl urls
st.markdown("## Obtención de urls")
if kit_digital.stages[StageType.CRAWL_URLS].status != StageStatus.PASS:
    kit_digital = crawl_urls(kit_digital)

# Show suggested urls
if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
    urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
    st.write(urls_stage.info["suggested_urls"])

# Select urls
st.markdown("## Seleccion de urls")
if kit_digital.stages[StageType.SELECT_URLS].status != StageStatus.PASS:
    kit_digital = select_urls(kit_digital)

# Show urls
if kit_digital.stages[StageType.SELECT_URLS].status == StageStatus.PASS:
    urls_stage: Stage = kit_digital.stages[StageType.SELECT_URLS]
    st.write(urls_stage.info["urls"])

st.markdown("## Subida a directorios")
# Directories
if kit_digital.stages[StageType.DIRECTORIES].status != StageStatus.PASS:
    kit_digital = directories(kit_digital)
    st.markdown("### Callupcontact")
    st.write(kit_digital.stages[StageType.CALLUPCONTACT])
    st.markdown("### Donde estamos")
    st.write(kit_digital.stages[StageType.DONDEESTAMOS])
    st.markdown("### Travelful")
    st.write(kit_digital.stages[StageType.TRAVELFUL])

# Show directories
if kit_digital.stages[StageType.DIRECTORIES].status == StageStatus.PASS:
    st.markdown("### Callupcontact")
    st.write(kit_digital.stages[StageType.CALLUPCONTACT])
    st.markdown("### Donde estamos")
    st.write(kit_digital.stages[StageType.DONDEESTAMOS])
    st.markdown("### Travelful")
    st.write(kit_digital.stages[StageType.TRAVELFUL])

# SEO Basico
st.markdown("## SEO Básico 1")
if kit_digital.stages[StageType.SEO_BASICO].status != StageStatus.PASS:
    kit_digital = set_seo_basico(kit_digital)

# Show SEO Basico
if kit_digital.stages[StageType.SEO_BASICO].status == StageStatus.PASS:
    st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["text_before_headers"])
    st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["text_after_headers"])
    st.markdown(kit_digital.stages[StageType.SEO_BASICO].info["multiidioma"])

# Headers SEO
st.markdown("## SEO Básico 2")
if kit_digital.stages[StageType.HEADERS_SEO].status != StageStatus.PASS:
    get_headers(kit_digital)

# Show Headers SEO
if kit_digital.stages[StageType.HEADERS_SEO].status == StageStatus.PASS:
    st.write(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h1"])
    st.write(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h2"])
    st.write(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h3"])

# Acreditacion cumplimiento en materia de publicidad
st.markdown("## Acreditación cumplimiento en materia de publicidad")
if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status != StageStatus.PASS:
    get_logo_kit(kit_digital)

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

# Plantilla de recopilacion de evidencias
st.markdown("## Plantilla de recopilación de evidencias 1: Pantallazos logo")
if kit_digital.stages[StageType.PANTALLAZOS_URLS].status != StageStatus.PASS:
    get_pantallazos_urls(kit_digital)

# Show Plantilla de recopilacion de evidencias
if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == StageStatus.PASS:
    with open(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["word"], "rb") as f:
        st.download_button(
            label="Descargar documento",
            data=f,
            file_name="pantallazos_urls.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


