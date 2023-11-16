#!/bin/bash

/usr/local/share/desktop-init.sh
xrandr -s 1280x720

cd web
/opt/conda/envs/web_env/bin/python /opt/conda/envs/web_env/bin/streamlit run app.py --server.port 8501 --server.headless True
