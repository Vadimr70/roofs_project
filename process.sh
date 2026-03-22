#!/usr/bin/env bash
PROCESS_DIR=$1 #folder to process

python3 rename.py --path=$PROCESS_DIR --layer='16'
python3 tools/infer_big_images.py all_locations outputs configs/hackathon/ocrnet_hrnet.py  weights/iter_12500.pth
python3 filter_masks.py
python3 get_table.py
python3 process_masks.py
python3 get_addresses_and_organisations.py