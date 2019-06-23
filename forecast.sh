#!/usr/bin/env bash

SELF_DIR=$(dirname $(realpath $0))

python3 ${SELF_DIR}/moneysheet.py \
        --input-file ${SELF_DIR}/sheetdata.py \
        --forecast-months 3
