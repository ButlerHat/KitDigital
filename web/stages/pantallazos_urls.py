import os
import datetime
import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import utils.robot_handler as robot_handler
import utils.notifications as notifications
import utils.remote_browser as remote_browser
from kitdigital import KitDigital, StageStatus, StageType, ChromeType
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
        st.warning("No se ha podido crear el word de recopilacion de evidencias.")
        # Send notification
        url: str = kit_digital.url
        kit_digital = send_contact_to_ntfy(kit_digital, f"Automatizacion word de evidencias (pantallazos logo). No ha funcionado la automatización para {url}.")
        kit_digital.stages[StageType.PANTALLAZOS_URLS].status = StageStatus.FAIL
        kit_digital.stages[StageType.PANTALLAZOS_URLS].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()
        return
    
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        stage = kit_digital.stages[StageType.PANTALLAZOS_URLS]
        stage.status = StageStatus.PASS
        stage.info["word"] = word_file
        kit_digital.stages[StageType.PANTALLAZOS_URLS] = stage
        kit_digital.to_yaml()
    
    else:
        kit_digital.stages[StageType.PANTALLAZOS_URLS].status = StageStatus.FAIL
        kit_digital.stages[StageType.PANTALLAZOS_URLS].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()


async def run_robot(kit_digital: KitDigital):
    """
    Get <h> labels from html.
    """
    results_path = kit_digital.stages[StageType.PANTALLAZOS_URLS].results_path
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if "urls" not in kit_digital.stages[StageType.SELECT_URLS].info:
        st.warning("Se deben obtener las urls de la página previamente.")
        st.stop()
    urls = kit_digital.stages[StageType.SELECT_URLS].info["urls"]

    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
    
    args = [
        f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
        f'UTILS_ENDPOINT:"{kit_digital.chrome_server.utils_endpoint}"',
        f'ORCHESTRATOR_ENDPOINT:"{st.secrets.urls.orchestrator}"',
        f'COOKIES_DIR:"{kit_digital.cookies_dir}"',
        f'URL:"{kit_digital.url}"',
        f'WORD_FILE:"{kit_digital.word_file}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"',
        *[f'url{i}:"{url}"' for i, url in enumerate(urls, start=1)]
    ]

    await robot_handler.run_robot(
        "pantallazos_urls", 
        args, 
        "KitD_Pantallazos/KitD_PantallazosUrls.robot", 
        output_dir=results_path,
        callbacks=[callback_pantallazos, notifications.callback_notify],
        kwargs_callbacks={"kit_digital": kit_digital},
        msg_info=f"Obteniendo pantallazos de la página: {kit_digital.url}"
    )


def get_pantallazos_urls(kit_digital: KitDigital) -> KitDigital:

    kit_digital.stages[StageType.PANTALLAZOS_URLS].status = StageStatus.PROGRESS
    kit_digital.to_yaml()
    
    # Get Browser
    kit_digital = remote_browser.get_browser(kit_digital, ChromeType.CDP, 'maximize')
    # Show browser
    kit_digital = remote_browser.show_browser(kit_digital, view_only=True)
    # Run robot
    asyncio.run(run_robot(kit_digital))  # Here store kit digital to yaml

    # Refresh kit digital
    kit_d = KitDigital.get_kit_digital(kit_digital.url)

    return kit_d if kit_d else kit_digital