#!/bin/bash

PT_CLOUD_TYPES=( pts_uni pts_annulus_random pts_ball pts_clusnorm pts_corners pts_normal pts_spokes )

mkdir tour-wds
mkdir path-wds

for type in ${PT_CLOUD_TYPES[@]}; do
    python src/main.py --minpts=10 --maxpts=1360 --interval=50 --numrunsper=50 --batch=50 --randtype="${type}"
    python src/read_simul_data.py --randtype="${type}"
done

rm -r tour-wds
rm -r path-wds
