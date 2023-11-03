import streamlit as st
from stages.directories import directories
from stages.crawl_urls import crawl_urls
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
    kit_digital.to_yaml()

# Show urls
if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
    urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
    st.write(urls_stage.info["suggested_urls"])

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


