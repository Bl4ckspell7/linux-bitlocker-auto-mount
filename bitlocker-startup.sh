#!/bin/bash

# Open a new terminal window and run the Python script with sudo.
# The -E flag preserves the user's environment variables, allowing Python to access installed packages.
gnome-terminal -- bash -c "echo 'Bitlocker auto-mount script is executing'; sudo -E python3 /SCRIPT_FOLDER_LOCATION/bitlocker-unlock-mount.py; exec bash"

