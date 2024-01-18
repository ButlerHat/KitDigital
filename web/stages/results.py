import os
import streamlit as st
import utils.pdf_utils as pdf_utils
from kitdigital import KitDigital, StageType



def show_results(kit_digital: KitDigital):
    # Url de la web
    st.markdown('## Textos de la memoria técnica')
    with st.expander('Memoria técnica', expanded=True):
        st.markdown('### URL')
        st.code(f"{kit_digital.url}", language='text')

        st.markdown('### Diseño de la página web')
        if kit_digital.stages[StageType.SELECT_URLS].status == "PASS":
            urls = kit_digital.stages[StageType.SELECT_URLS].info["urls"]
            text = f'Se ha estructurado el diseño web con {len(urls)} apartados que aquí detallamos:\n\n' + \
                '\n'.join([f'Página {i+1}. {url}' for i, url in enumerate(urls)])
            st.code(text, language='text')
        else:
            st.warning('Se deben obtener las urls de la página previamente. Haz el paso 2')

        st.markdown('### Posicionamiento básico en directorios')
        if kit_digital.stages[StageType.DIRECTORIES].status == "PASS":            
            directories: dict = kit_digital.stages[StageType.DIRECTORIES].info.get("directories", [])
            text = f'Además, hemos logrado posicionar la web en {len(directories)} directorios más:\n\n'
            if len(directories) > 0:
                text += '\n'.join([f'{i}. {directory.get("name", "")}: {directory.get("url", "")}' for i, directory in enumerate(directories, 1)])
            
            st.code(text, language='text')
        else:
            st.warning('Se debe subir la información de la empresa a 3 directorios. Haz el paso 3')

        st.markdown('### SEO básico')
        if kit_digital.stages[StageType.SEO_BASICO].status == "PASS" and \
            kit_digital.stages[StageType.HEADERS_SEO].status == "PASS":

            pt1 = kit_digital.stages[StageType.SEO_BASICO].info["text_before_headers"]
            pt2 = 'Página 1º Hemos asignado las etiquetas H1, H2 y H3 a los títulos y encabezados en la web' + \
                f' "{kit_digital.url}". Esto ayuda a que Google identifique las palabras clave prioritarias para ' + \
                'el cliente en todas las páginas del sitio.\n\n' + \
                '\n'.join(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h1"]) + '\n\n' + \
                '\n'.join(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h2"]) + '\n\n' + \
                '\n'.join(kit_digital.stages[StageType.HEADERS_SEO].info["suggested_h3"])
            pt3 = kit_digital.stages[StageType.SEO_BASICO].info["text_after_headers"]

            text = pt1 + '\n\n' + pt2 + '\n\n' + pt3
            st.code(text, language='text')
        else:
            st.warning('Se debe completar el SEO básico. Haz el paso 4 y 5')

        st.markdown('### Multidioma')
        if kit_digital.stages[StageType.SEO_BASICO].status == "PASS":
            text = kit_digital.stages[StageType.SEO_BASICO].info["multiidioma"]
            st.code(text, language='text')
        else:
            st.warning('Se debe completar el SEO básico. Haz el paso 4')

    
    st.markdown('## Pantallazos de la web')
    
    st.markdown('### Cumplimiento en materia de publicidad')
    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == "PASS":
        with st.expander('Pantallazos de la web', expanded=True):
            st.write('Capturas de pantalla que acreditan el cumplimiento en materia de publicidad (art. 34 BBRR)')
            with open(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["pdf"], "rb") as f:
                st.download_button(
                    label="Descargar documento",
                    data=f,
                    file_name="pantallazo_logo.pdf",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
    else:
        st.warning('Se debe hacer un pantallazo al logo de kit digital. Haz el paso 6')

    st.markdown('### Informe de accesibilidad')
    with st.expander('Informe de accesibilidad', expanded=True):
        st.write('Informe de revisión de la accesibilidad según el modelo disponible en Acelerapyme. NO es obligatorio para Segmento 1')
        if kit_digital.stages[StageType.LAST_TOUCHES].info.get('accesibilidad', None):
            with open(kit_digital.stages[StageType.LAST_TOUCHES].info["accesibilidad"], "rb") as f:
                st.download_button(
                    label="Descargar documento",
                    data=f,
                    file_name="accesibilidad.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning('Informe de accesibilidad no subido. Haga el paso 9')
        
    st.markdown('### Plantilla recopilación de evidencias')
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == "PASS" and \
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == "PASS":
        # Copy word to word_result
        assert os.path.exists(st.secrets.paths.word_template), f"La plantilla de word no existe. Consulte con el administrador"
        os.system(f"cp {st.secrets.paths.word_template} {kit_digital.word_file}")

        # Delete placeholders.
        with st.spinner('Generando word...'):
            # Insert hosting screenshots
            if kit_digital.stages[StageType.LAST_TOUCHES].info.get("hosting_screenshots", None):
                for hosting_screenshot in kit_digital.stages[StageType.LAST_TOUCHES].info["hosting_screenshots"]:
                    pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{INSERTAR_PANTALLAZOS_HOSTING}", "", hosting_screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "INSERTAR_PANTALLAZOS_HOSTING"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{INSERTAR_PANTALLAZOS_HOSTING}")
            else:
                st.warning('No se han subido pantallazos del hosting')

            # Insert autogestionable screenshots
            if kit_digital.stages[StageType.LAST_TOUCHES].info.get("web_screenshots", None):
                for web_screenshot in kit_digital.stages[StageType.LAST_TOUCHES].info["web_screenshots"]:
                    pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{CAPTURAS_AUTOGESTIONABLE}", "", web_screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "CAPTURAS_AUTOGESTIONABLE"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{CAPTURAS_AUTOGESTIONABLE}")
            else:
                st.warning('No se han subido pantallazos de la web autogestionable')

            # Insert urls screenshots
            if kit_digital.stages[StageType.PANTALLAZOS_URLS].info.get("screenshots", None):
                for i, screenshot in enumerate(kit_digital.stages[StageType.PANTALLAZOS_URLS].info["screenshots"]):
                    pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZOS_WEB}", f"Página {i}.", screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZOS_WEB"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZOS_WEB}")

            # Insert urls desktop
            if kit_digital.stages[StageType.PANTALLAZOS_URLS].info.get("desktop_screenshot", None):
                desktop_screenshot = kit_digital.stages[StageType.PANTALLAZOS_URLS].info["desktop_screenshot"]
                pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZO_WEB_ESCRITORIO}", "", desktop_screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZO_WEB_ESCRITORIO"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZO_WEB_ESCRITORIO}")

            # Insert urls mobile
            if kit_digital.stages[StageType.PANTALLAZOS_URLS].info.get("mobile_screenshot", None):
                mobile_screenshot = kit_digital.stages[StageType.PANTALLAZOS_URLS].info["mobile_screenshot"]
                pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZO_WEB_MOVIL}", "", mobile_screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZO_WEB_MOVIL"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZO_WEB_MOVIL}")

            # Insert urls ipad
            if kit_digital.stages[StageType.PANTALLAZOS_URLS].info.get("ipad_screenshot", None):
                ipad_screenshot = kit_digital.stages[StageType.PANTALLAZOS_URLS].info["ipad_screenshot"]
                pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZO_WEB_TABLETA}", "", ipad_screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZO_WEB_TABLETA"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZO_WEB_TABLETA}")

            # Insert multiidioma screenshots
            if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info.get("screenshots", None):
                for i, screenshot in enumerate(kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["screenshots"]):
                    pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZOS_MULTI-IDIOMA}", f"Página {i}.", screenshot)
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZOS_MULTI-IDIOMA"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZOS_MULTI-IDIOMA}")

            # Insert directories screenshots
            if kit_digital.stages[StageType.DIRECTORIES].info.get("directories", None):
                for directory in kit_digital.stages[StageType.DIRECTORIES].info["directories"]:
                    pdf_utils.append_text_and_picture_to_document(kit_digital.word_file, "{PANTALLAZOS_DIRECTORIOS}", directory.get("name", ""), directory.get("screenshot", ""))
                if pdf_utils.check_if_identifier_exists(kit_digital.word_file, "PANTALLAZOS_DIRECTORIOS"):
                    pdf_utils.remove_identifier(kit_digital.word_file, "{PANTALLAZOS_DIRECTORIOS}")

        with st.expander('Plantilla recopilación de evidencias', expanded=True):
            st.write('Plantilla para recopilar las evidencias de la web')
            with open(kit_digital.word_file, "rb") as f:
                st.download_button(
                    label="Descargar documento",
                    data=f,
                    file_name="evidencias.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
    else:
        st.warning('Se debe completar la plantilla de evidencias. Haz el paso 7 y 8')