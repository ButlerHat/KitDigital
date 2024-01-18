import streamlit as st
import extra_streamlit_components as stx
import streamlit.components.v1 as components
import requests

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookies_manager = get_manager()


def get_access_token_from_cookie() -> str:
    session_info = cookies_manager.get(cookie="access_token")
    if session_info:
        return session_info
    return ""


def button_click_action():
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code_values = query_params.get("code")
        if isinstance(code_values, list):
            return code_values
        else:
            return code_values
    return None


def Google_auth(clientId, clientSecret, redirect_uri):

    # Delete
    cookies = cookies_manager.get_all()
    st.write(cookies)

    access_token: str = get_access_token_from_cookie()

    # Signup
    if access_token == "":
        st.subheader("Google Authentication")
        auth_url = "https://accounts.google.com/o/oauth2/auth"
        client_id = clientId
        client_secret = clientSecret
        redirect_uri = redirect_uri
        scope = "https://www.googleapis.com/auth/userinfo.email"
        auth_endpoint = f"{auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
        custom_button = """
        <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
        crossorigin="anonymous"
        />
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <script
        src="https://code.jquery.com/jquery-3.2.1.slim.min.js"
        integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN"
        crossorigin="anonymous"
        ></script>
        <script
        src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
        integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl"
        crossorigin="anonymous"
        ></script>
        <style>
        .custom-button {
        width: 184px;
        height: 42px;
        background-color: #4285f4;
        border-radius: 2px;
        box-shadow: 0 3px 4px 0 rgba(0, 0, 0, 0.25);
        position: relative;
        cursor: pointer;
        border: 1px solid #fff; /* Light border for visibility on dark backgrounds */
        }
        .custom-button img {
        position: absolute;
        margin-top: 11px;
        margin-left: 11px;
        width: 18px;
        height: 18px;
        }
        .custom-button p {
        float: right;
        margin: 11px 11px 0 0;
        color: #fff;
        font-size: 14px;
        letter-spacing: 0.2px;
        font-family: 'Roboto', sans-serif;
        font-weight: bold;
        }
        </style>
        """ + f"""
        <div style="background: transparent;">
            <div class="custom-button" onclick="window.open('{auth_endpoint}', '_blank');">
                <div style="position: absolute; margin-top: 1px; margin-left: 1px; width: 40px; height: 40px; border-radius: 2px; background-color: #fff;">
                    <img src="https://pbs.twimg.com/profile_images/1605297940242669568/q8-vPggS_400x400.jpg" />
                </div>
                <p>Sign in with Google</p>
            </div>
        </div>
        """
        components.html(custom_button, height=42, width=184)
        security_code = button_click_action()

        if security_code:
            tokens = security_code
            token = ""
            for i in tokens:
                token += i
            verify_token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "code": security_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }

            response = requests.post(verify_token_url, data=payload)
            response_data = response.json()
            access_token: str = response_data.get("access_token")

            if response.status_code == 200:
                st.success(f"Login successfully")
                cookies_manager.set("access_token", access_token)

                # Delete
                cookies = cookies_manager.get_all()
                st.write(cookies)
        
    if access_token:
        profile_url = (
            "https://www.googleapis.com/oauth2/v1/userinfo?access_token="
            + access_token
            + ""
        )
        fetch_profile = requests.get(profile_url)
        if fetch_profile.status_code == 200:
            json_fetch_user_profile = fetch_profile.json()
            username = json_fetch_user_profile.get("email").split("@")[0].upper()
            st.write(f"Welcome! {username}")
            return json_fetch_user_profile
    
        else:
            st.warning("Login failed")
            return None
        
