#!/usr/bin/env sh

# Absolute path to this script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

PYTHONPATH="${SCRIPTPATH}" python3 "${SCRIPTPATH}/codenarrative/main.py" $*
