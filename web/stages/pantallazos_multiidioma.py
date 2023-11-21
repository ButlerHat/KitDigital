import os
import datetime
import asyncio
import pandas as pd
import numpy as np
import streamlit as st
import utils.remote_browser as remote_browser
import utils.robot_handler as robot_handler
import utils.notifications as notifications
from kitdigital import KitDigital, StageStatus, StageType
from utils.notifications import send_contact_to_ntfy



def callback_pantallazos(ret_val: int | None, result_path: str, kwargs_callbacks: dict, run_robot_kwargs: dict):  # pylint: disable=unused-argument
    """
    Store word after run robot.
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
        pabot=False,
        include_tags=[]
    Columns of msg_csv: id_execution, robot (without .robot), status, exception, msg
    """
    kit_digital: KitDigital = kwargs_callbacks["kit_digital"]

    # Get variables
    vars_ = run_robot_kwargs["vars_"]
    id_execution = [x for x in vars_ if "ID_EXECUTION" in x][0].split(":")[1].strip('"')
    msg_csv = [x for x in vars_ if "RETURN_FILE" in x][0].split(":")[1].strip('"')
    word_file = [x for x in vars_ if "WORD_FILE" in x][0].split(":")[1].strip('"')

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        st.warning("No se ha podido crear el word de recopilacion de evidencias de multiidioma.")
        # Send notification
        url: str = kit_digital.url
        kit_digital = send_contact_to_ntfy(kit_digital, f"Automatizacion word de evidencias (pantallazos multiidioma). No ha funcionado la automatización para {url}.")
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status = StageStatus.FAIL
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()
        return
    
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        # Set Url to Pass. Iterate 
        for row in df_pass.itertuples():
            try:
                kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info['urls'][row.msg] = "PASS"
            except KeyError:
                send_contact_to_ntfy(kit_digital, f"Error en automatizacion word de evidencias (pantallazos multiidioma). No se ha encontrado la url {row.msg} en el kit digital.")

        stage = kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA]
        stage.info["word"] = word_file
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA] = stage
        kit_digital.to_yaml()
    
    else:
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status = StageStatus.FAIL
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()

    # Check if all urls are in PASS
    if all([url == "PASS" for url in kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info['urls'].values()]):
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status = StageStatus.PASS
        kit_digital.to_yaml()

async def run_robot(kit_digital: KitDigital):
    """
    Get screenshots.
    """

    results_path = kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].results_path
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if "urls" not in kit_digital.stages[StageType.SELECT_URLS].info:
        st.warning("Se deben obtener las urls de la página previamente.")
        st.stop()
    urls = kit_digital.stages[StageType.SELECT_URLS].info["urls"]

    # Store urls in kit_digital
    for url in urls:
        if url not in kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info['urls'].keys():
            kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info['urls'][url] = "PENDING"
    
    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")

    # Check pending urls
    pending_urls = [url for url in urls if kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["urls"][url] != "PASS"]
    for url in pending_urls:
        st.info(f"Espere a la navegación a {url}. Por favor, cambie de idioma y después realice el pantallazo con el botón de abajo.")
        args = [
            f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
            f'UTILS_ENDPOINT:"{kit_digital.chrome_server.utils_endpoint}"',
            f'COOKIES_DIR:"{kit_digital.cookies_dir}"',
            f'URL:"{kit_digital.url}"',
            f'WORD_FILE:"{kit_digital.word_file}"',
            f'RETURN_FILE:"{msg_csv}"',
            f'ID_EXECUTION:"{id_execution}"',
            f'URL:"{url}"'
        ]

        if "executing_screenshots" not in st.session_state or not st.session_state["executing_screenshots"]:
            pl_warining = st.empty()
            await robot_handler.run_robot(
                "pantallazos_multiidioma", 
                args, 
                "KitD_Pantallazos/KitD_PantallazosUrlsMulti.robot", 
                output_dir=results_path,
                callbacks=[notifications.callback_notify],
                kwargs_callbacks={"kit_digital": kit_digital},
                msg_info="Obteniendo los pantallazos en multi-idioma. Por favor, haz click en el cambio de idioma.",
                include_tags=["1"]
            )
            pl_warining.empty()
            st.session_state["executing_screenshots"] = True
        
        # Put a button and wait for it to be clicked.
        st.markdown("## Cambia el idioma")
        placeholder = st.empty()
        if placeholder.button("Realiza el pantallazo"):
            placeholder.empty()
            await robot_handler.run_robot(
                "pantallazos_multiidioma",
                args, 
                "KitD_Pantallazos/KitD_PantallazosUrlsMulti.robot", 
                output_dir=results_path,
                callbacks=[callback_pantallazos, notifications.callback_notify],
                kwargs_callbacks={"kit_digital": kit_digital},
                msg_info=f"Capturando el patnallazo: {url}",
                include_tags=["2"]
            )
            st.session_state["executing_screenshots"] = False
            st.rerun()
        elif st.session_state["executing_screenshots"]:
            st.stop()
        
    # Check if kit_digital is finished. All urls are in PASS

    for info_key, info_value in kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info['ulrs'].items():
        
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status = StageStatus.PASS
        kit_digital.to_yaml()
        return


def get_pantallazos_multiidioma(kit_digital: KitDigital) -> KitDigital:

    if not "urls" in kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info:
        kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].info["urls"] = {}

    kit_digital.stages[StageType.PANTALLAZOS_MULTIIDIOMA].status = StageStatus.PROGRESS
    kit_digital.to_yaml()

    kit_digital = remote_browser.get_browser(kit_digital, remote_browser.ChromeType.CDP, 'maximize')
    remote_browser.show_browser(kit_digital, StageType.PANTALLAZOS_MULTIIDIOMA)
    asyncio.run(run_robot(kit_digital))  # Here store kit digital to yaml

    # Refresh kit digital
    kit_d = KitDigital.get_kit_digital(kit_digital.url)

    return kit_d if kit_d else kit_digital