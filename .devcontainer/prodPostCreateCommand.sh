#!/bin/bash

# Init VNC
xrandr -s 1280x720
# Install robot libraries
pip install --user -e /workspaces/ai-butlerhat/data-butlerhat/robotframework-butlerhat[browser_stealth]
