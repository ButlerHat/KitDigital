import requests
import asyncio
from typing import Literal
import streamlit as st
from kitdigital import ChromeType, KitDigital, ChromeServer
import utils.robot_handler as robot_handler
import streamlit.components.v1 as components


BASE_URL = st.secrets.urls.orchestrator
# BASE_URL = "http://192.168.85.2:31371"  # Kubernetes NodePort to send files greater than 100MB
# BASE_URL = "http://localhost:8000"

def _remove_toolbar(utils_endpoint: str):
    config_data = [
        "session.screen0.toolbar.visible: false"
    ]
    response = requests.post(utils_endpoint + "/change-fluxbox-config", json=config_data)
    return response


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
    
    # Configure options
    cdp_args = [
      "--start-fullscreen"
    ] if maximize_or_full == "full" else [
      "--start-maximized"
    ]

    playwright_options = {
        "headless": False,
        "args": [
            "--start-maximized",
        ]
    } if maximize_or_full == "full" else {
        "headless": False
    }

    try:
        # Is docker?
        if kit_digital.chrome_server:
            with st.spinner("Comprobando máquina virtual..."):
                res = requests.get(f"{BASE_URL}/is-alive/{kit_digital.chrome_server.id_}")
                if res.status_code != 200 or res.json()["is_alive"] == "false":
                    kit_digital.chrome_server = None

        # Is browser alive and correct type? If not alive, switch browser is enough
        if kit_digital.chrome_server and kit_digital.chrome_server.chrome_type == chrome_type:
            ret_val = asyncio.run(robot_handler.run_robot(
                "health_check",
                [f'WSENDPOINT:"{kit_digital.chrome_server.playwright_endpoint}"'],
                "healthcheck.robot",
                msg_info="Comprobando el navegador..."
            ))
            if ret_val != 0:
                kit_digital.chrome_server.chrome_type = ChromeType.EMPTY
                kit_digital.to_yaml()
                kit_digital = get_browser(kit_digital, chrome_type=chrome_type, maximize_or_full=maximize_or_full)
                return kit_digital
            else:
                return kit_digital
        
        # If not docker
        if not kit_digital.chrome_server:
            with st.spinner("Creando máquina virtual... Esto puede tardar unos segundos."):
                # First create a docker
                response = create_chromium_server()
                # Check if response is ok
                if "id_" not in response or "novnc_endpoint" not in response or "playwright_endpoint" not in response:
                    raise Exception("No se ha podido crear el navegador. No hay id_ o novnc_endpoint en la respuesta.")

                # Remove toolbar. This will remove the toolbar but browser will close
                _remove_toolbar(response["utils_endpoint"])

                kit_digital.chrome_server = ChromeServer(
                    **response, 
                    chrome_type=ChromeType.EMPTY
                )

        # Now open the browser with options and args
        assert kit_digital.chrome_server, "No se ha podido obtener el navegador."

        with st.spinner("Abriendo navegador... Espere unos segundos."):
            if chrome_type == ChromeType.PLAYWRIGHT:
                try:
                    response = switch_to_chromium_server(kit_digital.chrome_server, options=playwright_options)
                    kit_digital.chrome_server = ChromeServer(**response, chrome_type=chrome_type)
                    kit_digital.to_yaml()
                except Exception as e:
                    raise Exception("El navegador de playwright no ha podido abrirse.")
            elif chrome_type == ChromeType.CDP:
                try:
                    response = switch_to_chrome_cdp(kit_digital.chrome_server, args=cdp_args)
                    kit_digital.chrome_server = ChromeServer(**response, chrome_type=chrome_type)
                    kit_digital.to_yaml()
                except Exception as e:
                    raise Exception("El navegador de cdp no ha podido abrirse.")
            else:
                raise Exception("Tipo de navegador no soportado.")

    except Exception as e:
        requests.post(
            "https://notifications.paipaya.com/kit_digital_fail",
            headers={
                "X-Email": "paipayainfo@gmail.com",
                "Tags": "warning"
            },
            data=f"KitDigital: Error al obtener un navegor: {e}"
        )
        raise Exception("No se ha podido obtener el navegador: " + str(e))

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