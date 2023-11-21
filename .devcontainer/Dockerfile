FROM mcr.microsoft.com/devcontainers/miniconda:0-3 AS base

ARG UNAME=vscode
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG PYPI_USER
ARG PYPI_PASS

USER root

# Change timezone
ENV TZ='/usr/share/zoneinfo/Europe/Madrid'
RUN sudo ln -snf $TZ /etc/localtime && echo "Europe/Madrid" > /etc/timezone

# Install robotframework env
ENV PIP_EXTRA_INDEX_URL=https://$PYPI_USER:$PYPI_PASS@pypiserver.paipaya.com/

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends poppler-utils ffmpeg libsm6 libxext6 scrot

# Install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

ENV DBUS_SESSION_BUS_ADDRESS="autolaunch:" \
    VNC_RESOLUTION="1440x768x16" \
    VNC_DPI="96" \
    VNC_PORT="5901" \
    NOVNC_PORT="6080" \
    DISPLAY=":1" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8"

RUN mkdir -p /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital && chown -R $UNAME:$UNAME /workspaces
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital

RUN conda init
USER $UNAME

# Not copy to web/conda.yaml because web/ has root permissions
COPY web/conda.yaml ./web-conda.yaml
RUN umask 0002 && conda env create -n web_env -f ./web-conda.yaml

# Not copy to robotframework/conda.yaml because robotframework/ has root permissions
COPY robotframework/conda.yaml ./robotframework-conda.yaml
RUN umask 0002 && conda env create -n robotframework -f ./robotframework-conda.yaml
# Set conda env as default
RUN echo "source activate robotframework" >> ~/.bashrc  

RUN rm -rf web-conda.yaml robotframework-conda.yaml



FROM mcr.microsoft.com/devcontainers/miniconda:0-3 AS prod

USER root

# Install robotframework env
ENV PIP_EXTRA_INDEX_URL=https://$PYPI_USER:$PYPI_PASS@pypiserver.paipaya.com/

# Install robot libraries
RUN /opt/conda/condabin/conda run -n robotframework pip install robotframework-butlerhat[browser_stealth]

# Copy project files
COPY . /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital
WORKDIR /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital

# This is needed to avoid permissions errors when clonning with actions
RUN chown -R $UNAME:$UNAME /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat/TestSuites/KitDigital

USER root
RUN chmod -R a+rw /opt/conda/envs/robotframework/lib/python3.10/site-packages/Browser
RUN unset PIP_EXTRA_INDEX_URL

USER $UNAME
# For using npm installed in conda
ENV PATH=/opt/conda/envs/robotframework/bin:$PATH
RUN /opt/conda/envs/robotframework/bin/python -m Browser.entry init

ENV DBUS_SESSION_BUS_ADDRESS="autolaunch:" \
    VNC_RESOLUTION="1280x720x16" \
    VNC_DPI="96" \
    VNC_PORT="5901" \
    NOVNC_PORT="6080" \
    DISPLAY=":1" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8"

CMD ["bash", "./.devcontainer/prod/postCreateCommand.sh"]

