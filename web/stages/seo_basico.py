import streamlit as st
import urllib.parse
from kitdigital import KitDigital, StageStatus, StageType


def set_seo_basico(kit_digital: KitDigital) -> KitDigital:
    """
    Set seo basico stage.
    """
    st.markdown("## Descripcion del SEO Básico")

    stage_info: dict = kit_digital.stages[StageType.SEO_BASICO].info
    company_name_default: str = stage_info["company_name"] if "company_name" in stage_info else ""
    
    if company_name_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        company_name_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["company_name"]

    city_default: str = stage_info["city"] if "city" in stage_info else ""
    if city_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        city_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["city"]

    keywords_default: str = stage_info["keywords"] if "keywords" in stage_info else ""
    if keywords_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        keywords_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["keywords"]
    
    if len(keywords_default.split(",")) < 5:
        # Add empty keywords until 5
        keywords_default += ", " * (5 - len(keywords_default.split(",")))
    
    # Keywords to list
    keywords_list: list = keywords_default.split(",")

    with st.form("SEO Básico"):
        company_name = st.text_input("Nombre de la empresa", value=company_name_default)
        city = st.text_input("Ciudad", value=city_default)
        for i, keyword in enumerate(keywords_list):
            col1, col2, col3 = st.columns(3)
            col1.text_input("Palabra clave", value=keyword, key=f"keyword_{i}")
            col2.number_input("Búsquedas mensuales", value=0, key=f"keyword_searches_{i}")
            col3.text_input("Competitividad", value='Baja', key=f"keyword_competition_{i}")

        add_slash = "" if kit_digital.url.endswith("/") else "/"
        sitemap_url = st.text_input("Url del sitemap de la web.", value=kit_digital.url + add_slash + "sitemap_index.xml")
        google_search_console_url_def = f"https://search.google.com/search-console?resource_id={urllib.parse.quote_plus(kit_digital.url)}"
        google_search_console_url = st.text_input("Url de Google Search Console.", value=google_search_console_url_def)
        bing_webmaster_tools_url_def = f"https://www.bing.com/webmasters?siteUrl={urllib.parse.quote_plus(kit_digital.url)}"
        bing_webmaster_tools_url = st.text_input("Url de Bing Webmaster Tools.", value=bing_webmaster_tools_url_def)


        if st.form_submit_button("Enviar"):
            kit_digital.stages[StageType.SEO_BASICO].status = StageStatus.PROGRESS
            kit_digital.to_yaml()

            intro = f'Hemos elaborado un análisis de palabras clave relacionadas con "{company_name}" en {city}, se ha llevado a cabo utilizando la plataforma Sixtrix.com. Se han estudiado todas las palabras clave pertinentes para un entendimiento profundo del negocio.\n'
            keywords_template = """
Palabras clave: {keyword}
Búsquedas mensuales: {month_search}
Competitividad: {competitiveness}
--
"""
            plugin_rankmath: str = "\nHemos instalado el plugin Rankmath, una herramienta versátil que facilita la realización de todas las tareas SEO, incluyendo el análisis de legibilidad, la optimización de títulos y mucho más."

            text_after_headers = """
Y así con todas las páginas de la web para que Google vea cuáles son las palabras clave que más le interesa al cliente posicionar.

*Indexación

Se ha creado y se ha dado de alta el sitemap de la web: ({sitemap_url})

Se ha creado y dado de alta la página web en Google Search Console: ({google_search_console_url})

Se ha creado y dado de alta la página web en Bing Webmaster Tools: ({bing_webmaster_tools_url})
"""
            multiidioma = """
Hemos instalado el plugin en WordPress de traducción TranslatePress - Multilingual. Se agregó como idioma principal castellano, además un segundo idioma inglés (UK).
"""
            
            kit_digital.stages[StageType.SEO_BASICO].status = StageStatus.PASS
            kit_digital.stages[StageType.SEO_BASICO].info = {
                "company_name": company_name,
                "city": city,
                "keywords": ",".join([st.session_state[f"keyword_{i}"] for i in range(len(keywords_list))]),
                "text_before_headers": "".join([
                    intro, 
                    *[keywords_template.format(
                        keyword=st.session_state[f"keyword_{i}"],
                        month_search=st.session_state[f"keyword_searches_{i}"],
                        competitiveness=st.session_state[f"keyword_competition_{i}"]
                    ) for i in range(len(keywords_list))],
                    plugin_rankmath
                ]),
                "text_after_headers": text_after_headers.format(
                    sitemap_url=sitemap_url, 
                    google_search_console_url=google_search_console_url,
                    bing_webmaster_tools_url=bing_webmaster_tools_url
                ),
                "multiidioma": multiidioma
            }
            kit_digital.to_yaml()

    return kit_digital

def show_modiffy_results(kit_digital: KitDigital) -> KitDigital:
    """
    Show modiffy results.
    """
    st.markdown("## Resultados del SEO Básico")
    st.info("Puedes modificar los resultados del SEO Básico. Recuerda que si lo haces, debes de dar al botón de enviar.")

    with st.form('Cambiar Seo Básico'):
        st.markdown("### Texto antes de los headers")
        text_before_headers = st.text_area("Texto antes de los headers", kit_digital.stages[StageType.SEO_BASICO].info["text_before_headers"], height=1200)

        st.markdown("### Texto después de los headers")
        text_after_headers = st.text_area("Texto después de los headers", kit_digital.stages[StageType.SEO_BASICO].info["text_after_headers"], height=300)

        st.markdown("### Multiidioma")
        text_multi = st.text_area("Multiidioma", kit_digital.stages[StageType.SEO_BASICO].info["multiidioma"])

        if st.form_submit_button("Enviar"):
            kit_digital.stages[StageType.SEO_BASICO].info["text_before_headers"] = text_before_headers
            kit_digital.stages[StageType.SEO_BASICO].info["text_after_headers"] = text_after_headers
            kit_digital.stages[StageType.SEO_BASICO].info["multiidioma"] = text_multi
            kit_digital.to_yaml()
            st.success("Se ha modificado el SEO Básico.")

    return kit_digital