#!/bin/bash

SCRIPT_DIRECTORY="/path/to/script/directory" # e.g. /home/USER/linux-bitlocker-auto-mount

CMD="source \"$SCRIPT_DIRECTORY/python3-venv/bin/activate\"
python \"$SCRIPT_DIRECTORY/bitlocker-unlock-mount.py\"
exec bash"

# ────────────────────
# Choose your terminal
# ────────────────────
CMD="$CMD" gnome-terminal -- bash -c 'eval "$CMD"'
# CMD="$CMD" ptyxis -- bash -c 'eval "$CMD"'
# CMD="$CMD" blackbox-terminal -e bash -c 'eval "$CMD"'
