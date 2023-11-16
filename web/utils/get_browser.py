import requests
import asyncio
import streamlit as st
from kitdigital import KitDigital, StageType, StageStatus, ChromeServer
import utils.robot_handler as robot_handler
import streamlit.components.v1 as components


BASE_URL = "http://api-chrome.paipaya.com"
# BASE_URL = "http://localhost:8000"

def create_chromium_server():
    """Sends a request to create a new browser instance."""
    response = requests.post(f"{BASE_URL}/create-chromium-server")
    if response.status_code == 200:
        print(f"Browser created successfully. {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")
    
def create_chrome_cdp():
    """Sends a request to create a new browser instance."""
    response = requests.get(f"{BASE_URL}/create-chrome-cdp")
    if response.status_code == 200:
        print(f"Browser created successfully. {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")

def destroy_browser(id_):
    """Sends a request to destroy an existing browser instance."""
    response = requests.delete(f"{BASE_URL}/destroy-browser/{id_}")
    if response.status_code == 204:
        print("Browser destroyed successfully.")
    else:
        raise Exception(f"Failed to destroy browser: {response.status_code}, {response.text}")
    

def get_and_show_browser(kit_digital: KitDigital, stage: StageType) -> KitDigital:
    """Get the browser and show it in an iframe."""

    # Check if browser is alive
    if kit_digital.chrome_server:
        res = requests.get(f"{BASE_URL}/is-alive/{kit_digital.chrome_server.id_}")
        if not res.status_code == 200:
            kit_digital.chrome_server = None
        else:
            # Do health check with robot
            ret_val = asyncio.run(robot_handler.run_robot(
                "health_check",
                [f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"'],
                "healthcheck.robot",
                msg_info="Comprobando que el navegador está vivo..."
            ))
            if ret_val != 0:
                kit_digital.chrome_server = None
        
    if not kit_digital.chrome_server:
        try:
            with st.spinner("Creando navegador... Esto puede tardar unos segundos."):
                response = create_chrome_cdp()
            if "id_" not in response or "novnc_endpoint" not in response or "playwright_endpoint" not in response:
                raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
        except Exception as e:
            kit_digital.stages[stage].status = StageStatus.FAIL
            kit_digital.stages[stage].info["error"] = f"Fallo al crear el navegador: {e}."
            kit_digital.to_yaml()
            return kit_digital
        
        # Get id_ from response
        chrome_server = ChromeServer(
            id_ = response["id_"],
            novnc_endpoint = response["novnc_endpoint"],
            playwright_endpoint = response["playwright_endpoint"]
        )
        kit_digital.chrome_server = chrome_server
        kit_digital.to_yaml()

    # Get vnc_url from response
    vnc_url = kit_digital.chrome_server.novnc_endpoint + \
        "&password=vscode&autoconnect=true&resize=scale&reconnect=true"
    components.iframe(vnc_url, height=600, scrolling=True)

    return kit_digital

def delete_browser_after_stage(kit_digital: KitDigital) -> KitDigital:
    if not kit_digital.chrome_server:
        return kit_digital
    
    try:
        with st.spinner("Eliminando navegador..."):
            destroy_browser(kit_digital.chrome_server.id_)
            kit_digital.chrome_server = None
            kit_digital.to_yaml()
    except Exception as e:
        requests.post(
            "https://notifications.paipaya.com/kit_digital_fail",
            headers={
                "X-Email": "paipayainfo@gmail.com",
                "Tags": "warning"
            },
            data=f"Fallo en orchestrator. Nos e ha podido eliminar el navegador: {e}",
            timeout=15
        )
    
    return kit_digital

if __name__ == "__main__":
    # Create a new browser instance
    print("Creating browser instance...")
    # browser = create_chrome_cdp()
    browser = create_chromium_server()
    print(browser)

    # Destroy the browser instance
    destroy_browser(browser["id_"])