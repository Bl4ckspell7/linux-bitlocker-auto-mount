#!/bin/bash

SCRIPT_DIRECTORY="/path/to/script/directory" # e.g. $HOME/linux-bitlocker-auto-mount

gnome-terminal -- bash -c "source $SCRIPT_DIRECTORY/python3-venv/bin/activate && python $SCRIPT_DIRECTORY/bitlocker-unlock-mount.py; exec bash"
