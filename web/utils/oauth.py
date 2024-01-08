# import streamlit as st
# import pyrebase

# firebase_config = {
#   "apiKey": "AIzaSyAFtLAN9faQc01r8cQ5uMtaUMjiezf20PA",
#   "authDomain": "paypaya-platform.firebaseapp.com",
#   "projectId": "paypaya-platform",
#   "storageBucket": "paypaya-platform.appspot.com",
#   "messagingSenderId": "947045396186",
#   "appId": "1:947045396186:web:4665a9896f93084a03bfe3"
# }

# firebase = pyrebase.initialize_app(firebase_config)
# auth = firebase.auth()



import streamlit as st
from google_auth import Google_auth

client_id = "947045396186-n9lpd4b1kl8h8hp0h2vgv2pkdq9pta4o.apps.googleusercontent.com"
client_secret = "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"
redirect_uri = "http://localhost:8503"

login = Google_auth(
    clientId=client_id, clientSecret=client_secret, redirect_uri=redirect_uri
)

if login == "authenticated":
    st.success("hello")
    pass


