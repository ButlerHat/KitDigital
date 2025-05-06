FROM mcr.microsoft.com/devcontainers/miniconda:0-3

ARG UNAME=vscode
ARG PYPI_USER
ARG PYPI_PASS
ARG FIREBASE_CONFIG_BASE64

# Change timezone
ENV TZ='/usr/share/zoneinfo/Europe/Madrid'
RUN sudo ln -snf $TZ /etc/localtime && echo "Europe/Madrid" > /etc/timezone

# Install required system packages
RUN sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx

# Install robotframework env
ENV PIP_EXTRA_INDEX_URL=https://$PYPI_USER:$PYPI_PASS@pypiserver.paipaya.com/

RUN mkdir -p /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital && chown -R $UNAME:$UNAME /workspaces
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital

RUN conda init
USER $UNAME

# Not copy to robotframework/conda.yaml because robotframework/ has root permissions
COPY robotframework/conda.yaml ./robotframework-conda.yaml
RUN umask 0002 && conda env create -n robotframework -f ./robotframework-conda.yaml
# Install robot libraries (In local dev environment are binded to the host with pip install -e)
RUN /opt/conda/condabin/conda run -n robotframework pip install robotframework-butlerhat[browser_stealth]

# Not copy to web/conda.yaml because web/ has root permissions
COPY web/conda.yaml ./web-conda.yaml
RUN umask 0002 && conda env create -n web_env -f ./web-conda.yaml

RUN rm -rf web-conda.yaml robotframework-conda.yaml

# Install playwright
USER root
RUN chmod -R a+rw /opt/conda/envs/robotframework/lib/python3.10/site-packages/Browser
RUN unset PIP_EXTRA_INDEX_URL

USER $UNAME
# For using npm installed in conda. KitDigital only will be using orchestrator with browsers.
ENV PATH=/opt/conda/envs/robotframework/bin:$PATH
RUN /opt/conda/envs/robotframework/bin/python -m Browser.entry init --skip-browsers

# Copy project files
COPY --chown=$UNAME:$UNAME . /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital

# Set prod secrets
RUN rm web/.streamlit/secrets.toml && cp web/.streamlit/secrets.prod.toml web/.streamlit/secrets.toml

# Set firebase config
ENV FIREBASE_CONFIG_BASE64=$FIREBASE_CONFIG_BASE64

CMD ["bash", "./.devcontainer/prod/postCreateCommand.sh"]
