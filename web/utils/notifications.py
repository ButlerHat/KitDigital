# Description: Contact form for the web app
import os
import requests
import streamlit as st
from kitdigital import KitDigital

def callback_notify(ret_val: int | None, result_path: str, kwargs_callbacks: dict, params: dict):
    kit_digital: KitDigital = kwargs_callbacks["kit_digital"]
    id_ = params["id_"]

    # Send notification
    if ret_val != 0:
        log_file = os.sep.join([result_path, "log.html"])
        if os.path.exists(log_file):
            requests.put(
                "https://notifications.paipaya.com/kit_digital_fail", 
                data=open(log_file, 'rb'),
                headers={
                    "X-Email": "paipayainfo@gmail.com",
                    "Tags": "warning",
                    "Filename": f"{kit_digital.id}-{id_}_fail_manually.html",
                },
                timeout=15
            )
        else:
            robot = params["robot"]
            requests.post(
                "https://notifications.paipaya.com/kit_digital_fail",
                headers={
                    "X-Email": "paipayainfo@gmail.com",
                    "Tags": "warning"
                },
                data=f"{kit_digital.id}-{id_} ({robot}) failed manually. No hmtl log file found.",
                timeout=15
            )


def send_contact_to_ntfy(kit_digital: KitDigital, msg: str = "") -> KitDigital:
    """
    Send notification
    """
    st.markdown("# Error: Nos pondremos en contacto contigo")
    with st.form("Contacto"):
        st.write("Proporciona tu email para que nos pongamos en contacto contigo")
        email = st.text_input("Email")

        if st.form_submit_button("Enviar"):
            # Save info
            kit_digital.contact_email = email
            kit_digital.to_yaml()
            
            # Send notification
            requests.post(
                "https://notifications.paipaya.com/kit_digital_fail",
                headers={
                    "X-Email": "paipayainfo@gmail.com",
                    "Tags": "warning"
                },
                data=f"{msg}. El email del usuario es {email}.",
                timeout=15
            )
    
    return kit_digital