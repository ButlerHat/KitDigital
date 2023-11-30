import os
import asyncio
from PIL import Image
import utils.robot_handler as robot_handler
import utils.notifications as notifications
import utils.pdf_utils as pdf_utils
import utils.remote_browser as remote_browser
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from kitdigital import ChromeType, KitDigital, StageStatus, StageType
from utils.notifications import send_contact_to_ntfy


def callback_logo(ret_val: int | None, result_path: str, kwargs_callbacks: dict, run_robot_kwargs: dict):  # pylint: disable=unused-argument
    """
    Store headers after run robot.
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
    
    if ret_val is None and ret_val != 0:
        send_contact_to_ntfy(kit_digital, "Error al obtener el pantallazo del logo del kit digital.")

async def run_robot(kit_digital: KitDigital):
    """
    Get <h> labels from html.
    """
    results_path = kit_digital.stages[StageType.LOGO_KIT_DIGITAL].results_path

    if not kit_digital.chrome_server:
        raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
    
    args = [
        f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"',
        f'COOKIES_DIR:"{kit_digital.cookies_dir}"',
        f'URL:"{kit_digital.url}"',
    ]
    if "executing_logo" not in st.session_state or not st.session_state["executing_logo"]:
        pl_warining = st.empty()
        pl_warining.warning("Espere a que desaparezca este mensaje...")
        await robot_handler.run_robot(
            "logo_kit_digital", 
            args, 
            "KitD_Pantallazos/KitD_PantallazosLogo.robot", 
            output_dir=results_path,
            callbacks=[callback_logo, notifications.callback_notify],
            kwargs_callbacks={"kit_digital": kit_digital},
            msg_info=f"Obteniendo el pantallazo del logo del kit digital {kit_digital.url}"
        )
        st.success('Centra el logo ahora')
        pl_warining.empty()
        st.session_state["executing_logo"] = True

    st.markdown("## Centra el logo del kit digital en la página")
    placeholder = st.empty()
    st.info("Si no aparece la página, reinicia el paso con el botón de arriba a la derecha.")
    if placeholder.button("Realizar pantallazo"):
        placeholder.empty()
        if not kit_digital.chrome_server:
            raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
        
        logo_screenshot: str = os.path.join(results_path, "logo_screenshot.png")

        # Take screenshot
        remote_browser.take_os_screenshot(kit_digital.chrome_server, logo_screenshot)
        
        # Save Kit Digital
        kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"] = logo_screenshot
        kit_digital.to_yaml()
        st.session_state["executing_logo"] = False
        

def get_logo_kit(kit_digital: KitDigital) -> KitDigital:
    
    kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status = StageStatus.PROGRESS
    kit_digital.to_yaml()

    # Get Browser
    if not kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info.get("screenshot", None):
        kit_digital = remote_browser.get_browser(kit_digital, ChromeType.CDP)
        kit_digital = remote_browser.show_browser(kit_digital, view_only=False)
        asyncio.run(run_robot(kit_digital))  # Here store kit digital to yaml

    if  kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info.get("screenshot", None) and \
        kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status != StageStatus.PASS:
        
        st.success("Enmarca en un rectángulo el logo del kit digital en la página. No se completará el paso hasta que no se haga click en el botón Enviar.")
        kit_digital = draw_bbox_in_logo(kit_digital)
    
    # Check if pass
    if kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status == StageStatus.FAIL:
        send_contact_to_ntfy(kit_digital, "Error al obtener el pantallazo del logo del kit digital")
        return kit_digital

    # Refresh kit digital
    kit_d = KitDigital.get_kit_digital(kit_digital.url)

    return kit_d if kit_d else kit_digital

def draw_bbox_in_logo(kit_digital: KitDigital) -> KitDigital:
    
    stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.color_picker("Stroke color hex: ", "#FF0000")
    drawing_mode = st.selectbox(
        "Drawing tool:", ("rect", "point", "freedraw", "line", "circle", "transform")
    )
    image = Image.open(kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"])

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.0)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=image,  # type: ignore
        width=image.width,
        height=image.height,
        drawing_mode=drawing_mode if drawing_mode is not None else "rect",
        key="canvas",
    )

    if st.button("Enviar"):
        # Draw image_data of type numpy.ndarray: on top of image
        image_data = Image.fromarray(canvas_result.image_data)
        image_data = image_data.convert("RGBA")
        image = image.convert("RGBA")
        composite = Image.alpha_composite(image, image_data)
        screenshot_path = kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["screenshot"]
        composite.save(screenshot_path)

        # Convert to pdf
        results_path = kit_digital.stages[StageType.LOGO_KIT_DIGITAL].results_path
        pdf_file: str = os.path.join(results_path, "pantallazo_logo.pdf")
        pdf_utils.convert_img_to_pdf(screenshot_path, pdf_file)
        kit_digital.stages[StageType.LOGO_KIT_DIGITAL].info["pdf"] = pdf_file

        kit_digital.stages[StageType.LOGO_KIT_DIGITAL].status = StageStatus.PASS
        kit_digital.to_yaml()
        st.image(composite)

    return kit_digital