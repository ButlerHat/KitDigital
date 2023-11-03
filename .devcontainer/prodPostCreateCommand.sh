#!/bin/bash

# Init VNC
xrandr -s 1280x720

# Install robot libraries
pip install -e /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat[browser_stealth]
python -m Browser.entry init

# SI NO FUNCIONA HACERLO ASI. PERO DEBERIA ESTAR ENTORNO ACTIVADO POR DOCKERFILE .BASHRC:
# conda run -n robotframework pip install -e /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat[browser_stealth]
# conda run -n robotframework python -m Browser.entry init
