#!/bin/bash

PT_CLOUD_TYPES=( pts_uni pts_annulus_random pts_ball pts_clusnorm pts_corners pts_normal pts_spokes )

for type in ${PT_CLOUD_TYPES[@]}; do
    python src/simulation.py --minpts=10 --maxpts=1350 --interval=50 --batch=50 --numrunsper=50 --randtype="${type}"
    python src/read_simul_data.py --randtype="${type}"
done
