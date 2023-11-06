import streamlit as st
import urllib.parse
from kitdigital import KitDigital, StageStatus, StageType


def set_seo_basico(kit_digital: KitDigital) -> KitDigital:
    """
    Set seo basico stage.
    """
    st.markdown("## Descripcion del SEO Básico")

    stage_info: dict = kit_digital.stages[StageType.SEO_BASICO].info
    company_name_default: str = stage_info["company_name"] if stage_info is not None else ""
    
    if company_name_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        company_name_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["company_name"]

    city_default: str = stage_info["city"] if stage_info is not None else ""
    if city_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        city_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["city"]

    keywords_default: str = stage_info["keywords"] if stage_info is not None else ""
    if keywords_default == "" and "company_data" in kit_digital.stages[StageType.DIRECTORIES].info:
        keywords_default = kit_digital.stages[StageType.DIRECTORIES].info["company_data"]["keywords"]

    with st.form("SEO Básico"):
        company_name = st.text_input("Nombre de la empresa", value=company_name_default)
        city = st.text_input("Ciudad", value=city_default)
        keywords = st.text_input("Palabras clave (Separadas por coma)", value=keywords_default)
        sitemap_url = st.text_input("Url del sitemap de la web.", value=kit_digital.url + "/sitemap_index.xml")
        google_search_console_url_def = f"https://search.google.com/search-console?resource_id={urllib.parse.quote_plus(kit_digital.url)}"
        google_search_console_url = st.text_input("Url de Google Search Console.", value=google_search_console_url_def)
        bing_webmaster_tools_url_def = f"https://www.bing.com/webmasters?siteUrl={urllib.parse.quote_plus(kit_digital.url)}"
        bing_webmaster_tools_url = st.text_input("Url de Bing Webmaster Tools.", value=bing_webmaster_tools_url_def)


        if st.form_submit_button("Enviar"):
            kit_digital.stages[StageType.SEO_BASICO].status = StageStatus.PROGRESS
            kit_digital.to_yaml()

            intro = f'Hemos elaborado un análisis de palabras clave relacionadas con "{company_name}" en {city}, se ha llevado a cabo utilizando la plataforma Sixtrix.com. Se han estudiado todas las palabras clave pertinentes para un entendimiento profundo del negocio.'
            keywords_template = """
Palabras clave: {keyword}\n
Búsquedas mensuales:\n
Competitividad:\n
--\n
"""
            plugin_rankmath: str = "Hemos instalado el plugin Rankmath, una herramienta versátil que facilita la realización de todas las tareas SEO, incluyendo el análisis de legibilidad, la optimización de títulos y mucho más."

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
                "keywords": keywords,
                "text_before_headers": "\n".join([
                    intro, 
                    *[keywords_template.format(keyword=keyword) for keyword in keywords.split(",")],
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