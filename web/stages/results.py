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
            url_dondeestamos = kit_digital.stages[StageType.DONDEESTAMOS].info["url"]
            url_callupcontact = kit_digital.stages[StageType.CALLUPCONTACT].info["url"]
            url_travelful = kit_digital.stages[StageType.TRAVELFUL].info["url"]
            text = f'Hemos logrado posicionar la web en 3 distintos directorios, lo que contribuirá a aumentar ' +\
                'su presencia y visibilidad en internet como:\n\n' + \
                f'1. Donde-estamos: \n{url_dondeestamos}\n' + \
                f'2. Callupcontact: \n{url_callupcontact}\n' + \
                f'3. Travelful: \n{url_travelful}\n'
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
        st.warning('Aún está sin completar. Aquí está la plantilla')
        with open(st.secrets.paths.accessibility_excel, "rb") as f:
            st.download_button(
                label="Descargar documento",
                data=f,
                file_name="accesibilidad.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.markdown('### Plantilla recopilación de evidencias')
    if kit_digital.stages[StageType.PANTALLAZOS_URLS].status == "PASS" and \
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status == "PASS":
        # Copy word to word_result
        assert os.path.exists(kit_digital.word_file)
        os.system(f"cp {kit_digital.word_file} {kit_digital.word_file_result}")

        # Delete placeholders.
        with st.spinner('Eliminando placeholders...'):
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZOS_WEB"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZOS_WEB}")
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZO_WEB_ESCRITORIO"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZO_WEB_ESCRITORIO}")
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZO_WEB_MOVIL"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZO_WEB_MOVIL}")
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZO_WEB_TABLETA"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZO_WEB_TABLETA}")
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZOS_MULTI-IDIOMA"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZOS_MULTI-IDIOMA}")
            if pdf_utils.check_if_identifier_exists(kit_digital.word_file_result, "PANTALLAZOS_DIRECTORIOS"):
                pdf_utils.remove_identifier(kit_digital.word_file_result, "{PANTALLAZOS_DIRECTORIOS}")

        with st.expander('Plantilla recopilación de evidencias', expanded=True):
            st.write('Plantilla para recopilar las evidencias de la web')
            with open(kit_digital.word_file_result, "rb") as f:
                st.download_button(
                    label="Descargar documento",
                    data=f,
                    file_name="evidencias.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
    else:
        st.warning('Se debe completar la plantilla de evidencias. Haz el paso 7 y 8')