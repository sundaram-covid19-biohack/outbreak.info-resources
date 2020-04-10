#!/usr/bin/env bash
DIRNAME=$(dirname "$0")
source $DIRNAME/venv/bin/activate
python $DIRNAME/protocols_to_bioschemas.py "$@"
