from typing import Literal
import requests
import asyncio
import streamlit as st
from kitdigital import ChromeType, KitDigital, StageType, ChromeServer
import utils.robot_handler as robot_handler
import streamlit.components.v1 as components


BASE_URL = "http://api-chrome.paipaya.com"
# BASE_URL = "http://localhost:8000"

def create_chromium_server(options: dict = {}):
    """Sends a request to create a new browser instance."""
    body = {
        "options": options
    }
    
    response = requests.post(f"{BASE_URL}/create-chromium-server", json=body)
    if response.status_code == 200:
        print(f"Browser created successfully. {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")
    
def create_chrome_cdp(args: list = []):
    """Sends a request to create a new browser instance."""
    body = {
        "args": args
    }
    response = requests.post(f"{BASE_URL}/create-chrome-cdp", json=body)
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
    

def switch_to_chromium_server(
        browser: ChromeServer, 
        options: dict = {
            "headless": False,
            "wsPath": 'ws'
        }
    ):
    """Sends a request to create a new browser instance."""
    options = {"options": options}

    response = requests.post(f"{BASE_URL}/switch-to-chromium-server/{browser.id_}", json=options)
    if response.status_code == 200:
        print(f"Browser switched successfully successfully. {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")
    
def switch_to_chrome_cdp(browser: ChromeServer, args: list = []):
    """Sends a request to create a new browser instance."""
    body = {
        "args": args
    }

    response = requests.post(f"{BASE_URL}/switch-to-chrome-cdp/{browser.id_}", json=body)
    if response.status_code == 200:
        print(f"Browser switched successfully successfully. {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")
    
def take_os_screenshot(browser: ChromeServer, output_path: str):
    """Sends a request to create a new browser instance."""

    response = requests.get(f"{browser.utils_endpoint}/take-screenshot")
    if response.status_code == 200:
        # Screenshot in content
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Screenshot taken successfully. {output_path}")
    else:
        raise Exception(f"Failed to take screenshot: {response.status_code}, {response.text}")

def get_browser(
        kit_digital: KitDigital, 
        chrome_type: ChromeType = ChromeType.CDP, 
        maximize_or_full: Literal['maximize', 'full'] = 'maximize'
    ) -> KitDigital:
    
    """Get the browser and show it in an iframe."""
    cdp_args = [
      "--start-fullscreen"
    ] if maximize_or_full == "full" else [
      "--start-maximized"
    ]

    if kit_digital.chrome_server and kit_digital.chrome_server.chrome_type != chrome_type:
        with st.spinner("Cambiando de navegador... Espere unos segundos."):
            if chrome_type == ChromeType.PLAYWRIGHT:
                try:
                    response = switch_to_chromium_server(kit_digital.chrome_server)
                    kit_digital.chrome_server = ChromeServer(**response, chrome_type=chrome_type)
                    kit_digital.to_yaml()
                    return kit_digital
                except Exception as e:
                    # Try to create new
                    kit_digital.chrome_server = None
            elif chrome_type == ChromeType.CDP:
                try:
                    response = switch_to_chrome_cdp(kit_digital.chrome_server, args=cdp_args)
                    kit_digital.chrome_server = ChromeServer(**response, chrome_type=chrome_type)
                    kit_digital.to_yaml()
                    return kit_digital
                except Exception as e:
                    # Try to create new
                    kit_digital.chrome_server = None
            else:
                raise Exception("Tipo de navegador no soportado.")

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
                if chrome_type == ChromeType.PLAYWRIGHT:
                    response = create_chromium_server()
                elif chrome_type == ChromeType.CDP:
                    response = create_chrome_cdp(args=cdp_args)
                else:
                    raise Exception("Tipo de navegador no soportado.")
                
            if "id_" not in response or "novnc_endpoint" not in response or "playwright_endpoint" not in response:
                raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")
        except Exception as e:
            requests.post(
                "https://notifications.paipaya.com/kit_digital_fail",
                headers={
                    "X-Email": "paipayainfo@gmail.com",
                    "Tags": "warning"
                },
                data=f"KitDigital: Error al obtener un navegor: {e}"
            )
            return kit_digital
        
        # Get id_ from response
        chrome_server = ChromeServer(
            id_ = response["id_"],
            novnc_endpoint = response["novnc_endpoint"],
            playwright_endpoint = response["playwright_endpoint"],
            utils_endpoint = response["utils_endpoint"],
            chrome_type = chrome_type
        )
        kit_digital.chrome_server = chrome_server
        kit_digital.to_yaml()
    
    return kit_digital
    

def show_browser(kit_digital: KitDigital, view_only: bool = False) -> KitDigital:
    if not kit_digital.chrome_server:
        kit_digital = get_browser(kit_digital)
        assert kit_digital.chrome_server, "No se ha podido obtener el navegador."
    
    # Get vnc_url from response
    vnc_url = kit_digital.chrome_server.novnc_endpoint + \
        "&password=vscode&autoconnect=true&resize=scale&reconnect=true"
    if view_only:
        vnc_url += "&view_only=true&show_dot=true"
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
    browser = create_chrome_cdp()
    print(browser)

    # Destroy the browser instance
    destroy_browser(browser["id_"])