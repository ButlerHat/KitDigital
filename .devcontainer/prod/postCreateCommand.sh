#!/bin/bash

cd web
/opt/conda/envs/web_env/bin/python /opt/conda/envs/web_env/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless True
