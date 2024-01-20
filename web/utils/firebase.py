import os
import base64
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


@st.cache_data
def inicialize_app():
    credential_json_path = st.secrets.paths.firebase_secrets
    # Check if file exists
    if not os.path.exists(credential_json_path):
    # Check if json is in environment file in base64
        json_credential_b64 = os.environ.get("FIREBASE_CONFIG_BASE64")
        if not json_credential_b64:
            st.error("Firebase credentials not found. Please, contact the administrator.")
            st.stop()
            return
        
        byte_data = base64.b64decode(json_credential_b64)
        with open(credential_json_path, "wb") as f:
            f.write(byte_data)
        
    cred = credentials.Certificate(credential_json_path)
    firebase_admin.initialize_app(cred)

def check_user_and_kit(user_id, kit_id) -> str:
    # Use a service account
    db = firestore.client()

    # Function to check if a user ID exists in 'kit_digitals'
    # Check if user ID exists
    user_ref = db.collection('kit_digitals').document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        # print('User ID exists.')
        # If user exists, check if kit digital ID exists within 'kit_digitals'
        kit_ref = user_ref.collection('kit_digitals').document(kit_id)
        kit_doc = kit_ref.get()
        if kit_doc.exists:
            # print('Kit digital ID exists.')
            # Get website url from 
            return kit_doc.to_dict()['website']
        else:
            print('Kit digital ID does not exist.')
            st.error('Permission denied.')
            st.stop()
            return ''
    else:
        print('User ID does not exist.')
        st.error('Permission denied')
        st.stop()
        return ''


# Replace 'your_user_id' and 'your_kit_id' with the actual IDs you want to check
if __name__ == '__main__':
    inicialize_app()
    user_exists = check_user_and_kit('BNPNsn4ekWaLOZN4qv8Y6X5djs92', 'hsEoRlhzL6EooaCuIYd5')
    print(f'User exists: {user_exists}')
    user_exists = check_user_and_kit('SADFA', 'FSGSDF')
    print(f'User exists 2: {user_exists}')

