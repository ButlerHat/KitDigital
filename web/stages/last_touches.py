import os
import random
import streamlit as st
from kitdigital import KitDigital, StageStatus, StageType


def add_last_touches(kit_digital: KitDigital) -> KitDigital:
    """
    Add the last touches to the web app.
    """
    
    
    # INFORME DE ACCESIBILIDAD
    st.markdown("## 1. Informe de accesibilidad")
    col2, col1 = st.columns(2)
    if not kit_digital.stages[StageType.LAST_TOUCHES].info.get('accesibilidad', None):
        col1.warning('Aún está sin completar. Aquí está la plantilla')
        with open(st.secrets.paths.accessibility_excel, "rb") as f:
                col1.download_button(
                    label="Descargar ejemplo",
                    data=f,
                    file_name="accesibilidad.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        col1.success('Excel de accesibilidad subido. Aquí está el documento')
        with open(kit_digital.stages[StageType.LAST_TOUCHES].info["accesibilidad"], "rb") as f:
            col1.download_button(
                label="Descargar documento",
                data=f,
                file_name="accesibilidad.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    col2.info("Sube aquí el excel de accesibilidad")
    with col2.form('Informe de Accesibilidad'):
        uploaded_file = st.file_uploader("Adjunta el excel de accesibilidad", 
                                     type=["xlsx", "xls"])
        if st.form_submit_button('Subir'):
            if uploaded_file is not None:
                file_path: str = os.path.join(kit_digital.stages[StageType.LAST_TOUCHES].results_path, "accesibilidad.xlsx")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                kit_digital.stages[StageType.LAST_TOUCHES].info["accesibilidad"] = file_path
                kit_digital.to_yaml()
                st.rerun()

    
    # PANTALLAZOS HOSTING
    st.markdown("## 2. Pantallazos del hosting")    
    st.info("Sube aquí los pantallazos del hosting")
    with st.form('hosting_screenshots'):
        uploaded_file = st.file_uploader("Adjunta los pantallazos del hosting",["png", "jpg", "jpeg"])
        
        if st.form_submit_button('Subir'):
            if uploaded_file is not None:
                hosting_screenshots: list = kit_digital.stages[StageType.LAST_TOUCHES].info.get("hosting_screenshots", [])
                file_path: str = os.path.join(kit_digital.stages[StageType.LAST_TOUCHES].results_path, f"hosting_screenshot_{random.randint(0, 100000)}.png")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                kit_digital.stages[StageType.LAST_TOUCHES].info["hosting_screenshots"] = hosting_screenshots + [file_path]
                kit_digital.to_yaml()
            else:
                st.warning("No se ha subido ningún archivo")

    # Show
    if kit_digital.stages[StageType.LAST_TOUCHES].info.get("hosting_screenshots", None):
        st.success(f"Se han subido {len(kit_digital.stages[StageType.LAST_TOUCHES].info['hosting_screenshots'])} pantallazos")
        for i, hosting_screenshot in enumerate(kit_digital.stages[StageType.LAST_TOUCHES].info["hosting_screenshots"], start=1):
            with st.expander(f"Pantallazo {i}", expanded=False):
                st.image(hosting_screenshot)
    else:
        st.warning("No se ha subido ningún archivo")


    # PANTALLAZOS AUTOGESTIONABLE
    st.markdown("## 3. Pantallazos de la web autogestionable")
    st.info("Sube aquí los pantallazos de la web autogestionable")
    with st.form('web_screenshots'):
        uploaded_file = st.file_uploader("Adjunta los pantallazos de la web autogestionable",["png", "jpg", "jpeg"])
        
        if st.form_submit_button('Subir'):
            if uploaded_file is not None:
                web_screenshots: list = kit_digital.stages[StageType.LAST_TOUCHES].info.get("web_screenshots", [])
                file_path: str = os.path.join(kit_digital.stages[StageType.LAST_TOUCHES].results_path, f"web_screenshot_{random.randint(0, 100000)}.png")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                kit_digital.stages[StageType.LAST_TOUCHES].info["web_screenshots"] = web_screenshots + [file_path]
                kit_digital.to_yaml()
            else:
                st.warning("No se ha subido ningún archivo")
    
    # Show
    if kit_digital.stages[StageType.LAST_TOUCHES].info.get("web_screenshots", None):
        st.success(f"Se han subido {len(kit_digital.stages[StageType.LAST_TOUCHES].info['web_screenshots'])} pantallazos")
        for i, web_screenshot in enumerate(kit_digital.stages[StageType.LAST_TOUCHES].info["web_screenshots"], start=1):
            with st.expander(f"Pantallazo {i}", expanded=False):
                st.image(web_screenshot)
    else:
        st.warning("No se ha subido ningún archivo")
    
    # PANTALLAZOS AUTOGESTIONABLE
    st.markdown("## 4. Pantallazos de la web multi-idioma")
    col1, col2 = st.columns([3, 1])
    col1.info("Sube aquí los pantallazos de la justificación de la web multi-idioma")
    
    if col2.button("Reiniciar justificación multi-idioma", type='primary'):
        kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"] = []
        kit_digital.to_yaml()
        st.rerun()

    col1, col2 = st.columns(2)

    # First add tutorial
    with col2.expander("Tutorial", expanded=True):
        justification_multi_dir = st.secrets.paths.justificacion_multi_dir
        st.markdown("### Justificación de la web multi-idioma de ejemplo")
        st.info("En este ejemplo, se muestra como justificar que la web tiene multi-idioma en páginas hechas con Wordpress.")
        st.markdown("---")
        st.image(os.path.join(justification_multi_dir, "1.png"), caption="Pantallazo 1")
        st.markdown("*El beneficiario podrá seguir los siguientes pasos para añadir más idiomas, si lo desea")
        st.markdown("Paso 1. \nEl beneficiario debe ingresar al wordpress de su dominio. Luego ingresar al plugin del idioma, para añadir el idioma deseado cómo se ve en el ejemplo")
        st.image(os.path.join(justification_multi_dir, "2.png"), caption="Pantallazo 2")
        st.markdown("Luego de agregar el idioma deseado deslizarse a la parte inferior, guardar cambios.")
        st.image(os.path.join(justification_multi_dir, "3.png"), caption="Pantallazo 3")
        st.markdown("Paso 2. \nLuego deberá irse a la pestaña de traducción automática, y cambiar la opción a SI.")
        st.image(os.path.join(justification_multi_dir, "4.png"), caption="Pantallazo 4")
        st.markdown("Una vez cambiada seleccionar: DeepL, Free.")
        st.image(os.path.join(justification_multi_dir, "5.png"), caption="Pantallazo 5")
        st.markdown("Deslizarse a la parte inferior, para guardar cambios.")
        st.image(os.path.join(justification_multi_dir, "6.png"), caption="Pantallazo 6")
        st.markdown("Con ello se tiene, la página traducida como se muestra a continuación.")
        st.info("Los pantallazos siguientes se añaden en la justificación gracias al paso 8")

    if not kit_digital.stages[StageType.LAST_TOUCHES].info.get('justificacion_multi', None):
        kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"] = []

    with col1.form('Justificacion multi-idioma'):
        before: str = st.text_area("Texto antes de una imagen")
        uploaded_file = st.file_uploader("Adjunta los pantallazos de la justificación de la web multi-idioma",["png", "jpg", "jpeg"])
        after: str = st.text_area("Texto después de una imagen")

        if st.form_submit_button('Subir'):
            if before:
                kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"].append(before)

            if uploaded_file is not None:
                file_path: str = os.path.join(kit_digital.stages[StageType.LAST_TOUCHES].results_path, f"justificacion_multi_{random.randint(0, 100000)}.png")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"].append(file_path)

            if after:
                kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"].append(after)
            
            kit_digital.to_yaml()
            st.rerun()

    # Show
    if kit_digital.stages[StageType.LAST_TOUCHES].info.get("justificacion_multi", None):
        col1.success(f"Esta es la justificacion que se va a subir")
        for i, justificacion_multi in enumerate(kit_digital.stages[StageType.LAST_TOUCHES].info["justificacion_multi"], start=1):
            if os.path.exists(justificacion_multi):
                    col1.image(justificacion_multi)
            else:
                col1.markdown(justificacion_multi)
            
    else:
        col1.warning("No se ha subido ningún archivo")
    
    # COMPROBACIÓN DE RESULTADO
    if kit_digital.stages[StageType.LAST_TOUCHES].status != StageStatus.PASS and \
        kit_digital.stages[StageType.LAST_TOUCHES].info.get('accesibilidad', None) and \
        kit_digital.stages[StageType.LAST_TOUCHES].info.get('hosting_screenshots', None) and \
        kit_digital.stages[StageType.LAST_TOUCHES].info.get('web_screenshots', None) and \
        kit_digital.stages[StageType.LAST_TOUCHES].info.get('justificacion_multi', None):

        kit_digital.stages[StageType.LAST_TOUCHES].status = StageStatus.PASS
        kit_digital.to_yaml()
    
    return kit_digital






