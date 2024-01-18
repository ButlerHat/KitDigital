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
    stage: StageType = kwargs_callbacks["stage"]
    urls: list = kwargs_callbacks["urls"]
    capture_mobile: bool = kwargs_callbacks["capture_mobile"]

    # Get variables
    vars_ = run_robot_kwargs["vars_"]
    id_execution = [x for x in vars_ if "ID_EXECUTION" in x][0].split(":")[1].strip('"')
    msg_csv = [x for x in vars_ if "RETURN_FILE" in x][0].split(":")[1].strip('"')

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        st.warning("No se ha podido crear el word de recopilacion de evidencias.")
        # Send notification
        url: str = kit_digital.url
        kit_digital = send_contact_to_ntfy(kit_digital, f"Automatizacion word de evidencias (pantallazos logo). No ha funcionado la automatización para {url}.")
        kit_digital.stages[stage].status = StageStatus.FAIL
        kit_digital.stages[stage].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()
        return
    
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        # Check if there are len(result_path/*.png) - 3 == len(urls)
        assert os.path.exists(result_path)
        # Get screenshots files which ends with .png and starts with a number
        url_screenshots = [x for x in os.listdir(result_path) if x.endswith(".png") and x[0].isdigit()]
        url_screenshots.sort(key=lambda x: int(x.split(".")[0]))
        
        if len(url_screenshots) == len(urls):
            # Sort screenshots by number
            stage_ = kit_digital.stages[stage]
            stage_.info["screenshots"] = [os.path.join(result_path, x) for x in url_screenshots]
            if capture_mobile:
                stage_.info["desktop_screenshot"] = os.path.join(result_path, "desktop_screenshot.png")
                stage_.info["mobile_screenshot"] = os.path.join(result_path, "mobile_screenshot.png")
                stage_.info["ipad_screenshot"] = os.path.join(result_path, "ipad_screenshot.png")
            stage_.status = StageStatus.PASS
            kit_digital.stages[stage] = stage_
            kit_digital.to_yaml()
            return

    kit_digital.stages[stage].status = StageStatus.FAIL
    kit_digital.stages[stage].info["error"] = "Fallo robotframework."
    kit_digital.to_yaml()


async def run_robot(
        kit_digital: KitDigital, 
        stage: StageType, 
        urls: list, 
        capture_mobile: bool = True
    ):
    """
    Get <h> labels from html.
    """
    results_path = kit_digital.stages[stage].results_path
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    if not urls:
        st.warning("Se deben obtener las urls de la página previamente.")
        st.stop()

    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
    
    args = [
        f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
        f'UTILS_ENDPOINT:"{kit_digital.chrome_server.utils_endpoint}"',
        f'ORCHESTRATOR_ENDPOINT:"{st.secrets.urls.orchestrator}"',
        f'COOKIES_DIR:"{kit_digital.cookies_dir}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"',
        *[f'url{i}:"{url}"' for i, url in enumerate(urls, start=1)],
        f'CAPTURE_MOBILE:"{capture_mobile}"'
    ]

    await robot_handler.run_robot(
        "pantallazos_urls", 
        args, 
        "KitD_Pantallazos/KitD_PantallazosUrls.robot", 
        output_dir=results_path,
        callbacks=[callback_pantallazos, notifications.callback_notify],
        kwargs_callbacks={
            "kit_digital": kit_digital,
            "stage": stage,
            "urls": urls,
            "capture_mobile": capture_mobile
        },
        msg_info=f"Obteniendo pantallazos de la página: {kit_digital.url}"
    )


def get_pantallazos_urls(
        kit_digital: KitDigital, 
        urls: list, 
        stage: StageType = StageType.PANTALLAZOS_URLS, 
        capture_mobile: bool = True
    ) -> KitDigital:

    kit_digital.stages[stage].status = StageStatus.PROGRESS
    kit_digital.to_yaml()
    
    # Get Browser
    kit_digital = remote_browser.get_browser(kit_digital, ChromeType.CDP, 'maximize')
    # Show browser
    kit_digital = remote_browser.show_browser(kit_digital, view_only=True)
    # Remove all screenshots from previous executions (and contents)
    screenshots_path = os.path.join(kit_digital.stages[stage].results_path)
    os.system(f"rm -rf {screenshots_path}/*")
    # Run robot
    asyncio.run(run_robot(kit_digital, stage, urls, capture_mobile))  # Here store kit digital to yaml

    # Refresh kit digital
    kit_d = KitDigital.get_kit_digital(kit_digital.url)

    return kit_d if kit_d else kit_digital