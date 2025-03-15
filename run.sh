#!/bin/sh

cd ~/files/emircargo
source .venv/bin/activate
python src/main.py DEBUG=0 HEADLESS=1
