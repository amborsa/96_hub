#!/bin/bash
lxterminal -t "app"  -e python3 /home/pi/96_hub/app.py  &
lxterminal -t "serial" -e python3 /home/pi/96_hub/serialreader.py 1 &

sleep 3


chromium-browser http://localhost:5000 --start-fullscreen
