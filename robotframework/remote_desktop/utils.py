import os
import requests
import time
from typing import Literal
from robot.libraries.BuiltIn import BuiltIn

def take_os_screenshot(utils_endpoint: str, output_path: str, bbox: tuple | None = None, resolution: str | None = None, wait: int = 1):
    """
    Sends a request to create a new browser instance. You can specify the resolution in fromat "widthxheight".
    """
    url = f"{utils_endpoint}/take-screenshot"
    if bbox is not None:
        if isinstance(bbox, tuple) and len(bbox) == 4:
            bbox_str = ','.join(map(str, bbox))
            url += f'/{bbox_str}'
        else:
            raise ValueError("bbox must be a tuple of four integers (x, y, width, height)")


    # Get current resolution
    current_resolution = "1280x720"
    if resolution is not None:
        current_resolution = get_current_resolution(utils_endpoint)
        
        # Set new resolution
        change_resolution(utils_endpoint, resolution)

        # After changing resolution, wait some seconds
        time.sleep(wait)
    
    response = requests.get(url)
    if response.status_code == 200:
        # Screenshot in content
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Screenshot taken successfully. {output_path}")
    else:
        raise Exception(f"Failed to take screenshot: {response.status_code}, {response.text}")
    
    if resolution is not None:
        # Restore resolution
        change_resolution(utils_endpoint, current_resolution)


def get_current_resolution(utils_endpoint: str) -> str:
    """
    Sends a request to create a new browser instance.
    """

    response = requests.get(f"{utils_endpoint}/get-current-resolution")
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to get current resolution: {response.status_code}, {response.text}")
    

def change_resolution(utils_endpoint: str, resolution: str):
    """
    Sends a request to create a new browser instance. You can specify the resolution in fromat "widthxheight".
    """

    response = requests.get(f"{utils_endpoint}/change-desktop-resolution/{resolution}")
    if response.status_code == 204:
        print(f"Resolution set successfully: {resolution}")
    else:
        raise Exception(f"Failed to set resolution: {response.status_code}, {response.text}")


def change_chrome_cdp_in_device(
        orchestrator_endpoint: str, 
        wsendpoint: str, 
        device: Literal["desktop", "ipad", "iphone"], 
        args: list = [
            '--start-maximized'
        ]
    ) -> dict:
    """
    Switch to chrome with desired chrome data dir. Returns a CPD instance.
    """
    # Get browser id from ws endpoint
    browser_id = wsendpoint.split("playwright_")[-1].split("/")[0]

    current_dir = os.path.dirname(os.path.realpath(__file__))
    user_data_dir_zip = ""
    if device == "desktop":
        user_data_dir_zip = os.path.join(current_dir, "desktop-user-dir.zip")
    elif device == "ipad":
        user_data_dir_zip = os.path.join(current_dir, "ipad-mini-user-dir.zip")
    elif device == "iphone":
        user_data_dir_zip = os.path.join(current_dir, "iphone-se-user-dir.zip")
    else:
        raise Exception(f"Unknown chrome data dir: {device}")
     
    response = switch_to_chrome_cdp_with_datadir(orchestrator_endpoint, browser_id, user_data_dir_zip, args)

    # Use utils endpoint to send F12 key to open dev tools
    utils_endpoint = response["utils_endpoint"]
    open_close_dev_tools(utils_endpoint)

    BuiltIn().set_variable("${WSENDPOINT}", response["playwright_endpoint"])
    BuiltIn().set_global_variable("${WSENDPOINT}", response["playwright_endpoint"])
    BuiltIn().log_to_console(f"Set WSENDPOINT to {response['playwright_endpoint']}")
    BuiltIn().run_keyword("Connect To Browser Over Cdp", "${WSENDPOINT}")
        
    return {
        "browser_id": response["id_"], 
        "playwright_endpoint": response["playwright_endpoint"], 
        "utils_endpoint": response["utils_endpoint"]
    }

def open_close_dev_tools(utils_endpoint: str):
    """
    Sends a request to create a new browser instance.
    """
    response = requests.get(f"{utils_endpoint}/press-keys/F12")
    if response.status_code == 200:
        print("Success:", response.json())
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")

def switch_to_chrome_cdp_with_datadir(
        orchestator_endpoint: str, 
        browser_id: str, 
        user_data_dir_zip: str,
        args: list = []
    ):
    
    """Sends a request to create a new browser instance."""
    body = {"args": args}

    files = {'userDataZip': open(user_data_dir_zip, 'rb')}

    response = requests.post(f"{orchestator_endpoint}/switch-to-chrome-cdp-datadir/{browser_id}", data=body, files=files)
    
    if response.status_code == 200:
        print("Success:", response.json())
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        raise Exception(f"Failed to create browser: {response.status_code}, {response.text}")
    

if __name__ == "__main__":
    BASE_URL = "http://api-chrome.paipaya.com"

    # Use utils endpoint to send F12 key to open dev tools
    # change_chrome_cdp_in_device(BASE_URL, browser["id_"], "desktop")
