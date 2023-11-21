import os
import asyncio
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import utils.robot_handler as robot_handler
import utils.remote_browser as remote_browser
import utils.notifications as notifications
from kitdigital import KitDigital, Stage, StageStatus, StageType


def callback_crawl(ret_val: int | None, result_path: str, kwargs_callbacks: dict, run_robot_kwargs: dict):  # pylint: disable=unused-argument
    """
    If robot fails, have a recovery.
    ret_val: int | None - return code of robot
    result_path: str - path where results are stored
    kwargs_callbacks: dict - kwargs of callbacks
    Arguments in run_robot_kwargs:
        id_: str, 
        vars_: list, 
        robot: str, 
        output_dir: str | None = None, 
        callback: list[Callable[[dict], None]] = [],
        kwargs_callbacks: dict = {},
        msg_file: str | None = None,
        msg_info=None, 
        msg_fail=None, 
        msg_success="Robot finished successfully", 
        pabot=False, 
        include_tags=[]
    Columns of msg_csv: id_execution, robot (without .robot), status, exception, msg
    """
    kit_digital: KitDigital = kwargs_callbacks["kit_digital"]

    # Get variables
    vars_ = run_robot_kwargs["vars_"]
    id_execution = [x for x in vars_ if "ID_EXECUTION" in x][0].split(":")[1].strip('"')
    msg_csv = [x for x in vars_ if "RETURN_FILE" in x][0].split(":")[1].strip('"')

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        return

    # Check if status is PASS
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        urls = []
        for row in df_pass.itertuples():
            # Get stage
            urls.append(row.msg)
        
        stage = kit_digital.stages[StageType.CRAWL_URLS]
        stage.status = StageStatus.PASS
        stage.info["suggested_urls"] = urls
        kit_digital.stages[StageType.CRAWL_URLS] = stage
        kit_digital.to_yaml()
    
    # Check if status is FAIL
    if ret_val != 0:
        stage = kit_digital.stages[StageType.CRAWL_URLS]
        stage.status = StageStatus.FAIL
        stage.info["error"] = "Fallo robotframework."
        kit_digital.stages[StageType.CRAWL_URLS] = stage
        kit_digital.to_yaml()


def run_robot(kit_digital: KitDigital, results_path: str) -> int | None:
    
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")

    args = [
        f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
        f'URL:"{kit_digital.stages[StageType.CRAWL_URLS].info["url_crawl"]}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"',
        f'FILTER_ENDING:"{kit_digital.stages[StageType.CRAWL_URLS].info["filter_ending"]}"'
    ]

    ret_code = asyncio.run(robot_handler.run_robot(
        "paginas", 
        args, 
        "KitD_Paginas.robot", 
        output_dir=results_path,
        callbacks=[callback_crawl, notifications.callback_notify],
        kwargs_callbacks={"kit_digital": kit_digital},
        msg_info=f"Obteniendo páginas de {kit_digital.stages[StageType.CRAWL_URLS].info['url_crawl']}. No cierre ni refresque la página, esto puede tardar de 1 a 2 minutos."
    ))

    return ret_code


def crawl_urls(kit_digital: KitDigital) -> KitDigital:
    # Create Urls Stage
    urls_stage: Stage = kit_digital.stages[StageType.CRAWL_URLS]
    urls_stage.status = StageStatus.PROGRESS
    kit_digital.stages[StageType.CRAWL_URLS] = urls_stage
    kit_digital.to_yaml()

    kit_digital.stages[StageType.CRAWL_URLS].info["url_crawl"] = kit_digital.url
    kit_digital.stages[StageType.CRAWL_URLS].info["filter_ending"] = True
    url_selected = False
    with st.form("Url a parti de donde buscar"):
        url: str = st.text_input("Url a parti de donde buscar", value=kit_digital.url)
        st.info("Filtrar por extensión puede ser útil para páginas que tienen muchos enlaces. Puedes probar primero sin filtrar y reiniciar el stage.")
        filter_ending: bool = st.checkbox("Filtrar por extensión", value=False)
        if st.form_submit_button("Enviar"):
            kit_digital.stages[StageType.CRAWL_URLS].info["url_crawl"] = url
            kit_digital.stages[StageType.CRAWL_URLS].info["filter_ending"] = filter_ending
            kit_digital.to_yaml()
            url_selected = True
    
    if url_selected:
        # Get Browser
        kit_digital = remote_browser.get_browser(kit_digital, remote_browser.ChromeType.PLAYWRIGHT)
        run_robot(kit_digital, urls_stage.results_path)  # Here store kit digital to yaml

    # Refresh kit digital
    kit_d: KitDigital | None = KitDigital.get_kit_digital(kit_digital.url)
    kit_digital = kit_d if kit_d else kit_digital

    return kit_digital


def select_urls(kit_digital: KitDigital) -> KitDigital:
    # Create Urls Stage
    urls_stage: Stage = kit_digital.stages[StageType.SELECT_URLS]
    kit_digital.stages[StageType.SELECT_URLS] = urls_stage
    kit_digital.to_yaml()

    # Ask for valid urls
    if kit_digital.stages[StageType.CRAWL_URLS].status == StageStatus.PASS:
        suggested_urls = kit_digital.stages[StageType.CRAWL_URLS].info["suggested_urls"]
        st.markdown("### Selecciona las urls válidas")
        with st.form("Selecciona las urls válidas"):
            urls = st.multiselect("Selecciona las urls válidas", suggested_urls)
            if st.form_submit_button("Enviar"):
                stage = kit_digital.stages[StageType.SELECT_URLS]
                stage.status = StageStatus.PASS
                stage.info["urls"] = urls
                kit_digital.stages[StageType.SELECT_URLS] = stage
                kit_digital.to_yaml()

    else:
        st.warning("Se deben obtener las urls de la página previamente.")
        st.stop()

    return kit_digital