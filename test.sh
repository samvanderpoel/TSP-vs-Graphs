#!/bin/bash

mkdir tour-wds
mkdir path-wds

python src/main.py --minpts=10 --maxpts=110 --interval=50 --numrunsper=50 --batch=50 --randtype=pts_uni
python src/read_simul_data.py --randtype=pts_uni

rm -r tour-wds
rm -r path-wds
