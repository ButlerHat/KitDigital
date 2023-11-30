import os
import datetime
import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import utils.robot_handler as robot_handler
import utils.notifications as notifications
import utils.remote_browser as remote_browser
from kitdigital import ChromeType, KitDigital, StageStatus, StageType
from utils.notifications import send_contact_to_ntfy


def callback_cookies(ret_val: int | None, result_path: str, kwargs_callbacks: dict, run_robot_kwargs: dict):  # pylint: disable=unused-argument
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

    df = pd.read_csv(msg_csv)
    # Get the row with id_execution = id_execution. If is empty, return
    df_id = df[df["id_execution"] == np.int64(id_execution)]
    if len(df_id) == 0:
        st.warning("No se han podido aceptar las cookies.")
        # Send notification
        url: str = kit_digital.url
        kit_digital = send_contact_to_ntfy(kit_digital, f"Error en aceptar las cookies. No ha funcionado la automatización para {url}.")
        kit_digital.stages[StageType.ACCEPT_COOKIES].status = StageStatus.FAIL
        kit_digital.stages[StageType.ACCEPT_COOKIES].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()
        return
    
    df_pass = df_id[df_id["status"] == "PASS"]
    if len(df_pass) > 0:
        stage = kit_digital.stages[StageType.ACCEPT_COOKIES]
        stage.status = StageStatus.PASS
        kit_digital.stages[StageType.ACCEPT_COOKIES] = stage
        kit_digital.to_yaml()
    
    else:
        kit_digital.stages[StageType.ACCEPT_COOKIES].status = StageStatus.FAIL
        kit_digital.stages[StageType.ACCEPT_COOKIES].info["error"] = "Fallo robotframework."
        kit_digital.to_yaml()


async def run_robot(kit_digital: KitDigital):
    """
    Get <h> labels from html.
    """
    results_path = kit_digital.stages[StageType.ACCEPT_COOKIES].results_path
    msg_csv: str = os.path.join(results_path, "msg.csv")
    robot_handler.create_csv(msg_csv)
    id_execution = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")

    args = [
        f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
        f'COOKIES_DIR:"{kit_digital.cookies_dir}"',
        f'URL:"{kit_digital.url}"',
        f'RETURN_FILE:"{msg_csv}"',
        f'ID_EXECUTION:"{id_execution}"',
    ]

    if "executing_cookies" not in st.session_state or not st.session_state["executing_cookies"]:
        await robot_handler.run_robot(
            "accept_cookies", 
            args, 
            "KitD_Cookies.robot", 
            output_dir=results_path,
            callbacks=[notifications.callback_notify],
            kwargs_callbacks={"kit_digital": kit_digital},
            msg_info=f"Acepta las cookies en la página: {kit_digital.url}",
            include_tags=["1"]
        )
        st.success('Accepta las cookies ahora')
        st.session_state["executing_cookies"] = True


    # Put a button and wait for it to be clicked.
    st.info("Si no aparece la página, reinicia el paso con el botón de arriba a la derecha.")
    st.markdown("## Acepta las cookies en la página")
    placeholder = st.empty()
    if placeholder.button("Guardar cookies"):
        placeholder.empty()
        await robot_handler.run_robot(
            "accept_cookies", 
            args, 
            "KitD_Cookies.robot", 
            output_dir=results_path,
            callbacks=[callback_cookies, notifications.callback_notify],
            kwargs_callbacks={"kit_digital": kit_digital},
            msg_info=f"Aceptando las cookies: {kit_digital.url}",
            include_tags=["2"]
        )
        st.session_state["executing_cookies"] = False


def accept_cookies(kit_digital: KitDigital) -> KitDigital:

    kit_digital.stages[StageType.ACCEPT_COOKIES].status = StageStatus.PROGRESS
    kit_digital.to_yaml()
    
    # Get Browser
    kit_digital = remote_browser.get_browser(kit_digital, ChromeType.CDP)
    # Show browser
    kit_digital = remote_browser.show_browser(kit_digital, view_only=False)
    asyncio.run(run_robot(kit_digital))  # Here store kit digital to yaml

    # Refresh kit digital
    kit_d = KitDigital.get_kit_digital(kit_digital.url)

    return kit_d if kit_d else kit_digital