#!/bin/bash

PT_CLOUD_TYPES=( pts_uni pts_annulus_random pts_ball pts_clusnorm pts_corners pts_grid pts_normal pts_spokes )
#PT_CLOUD_TYPES=( pts_uni )

for type in ${PT_CLOUD_TYPES[@]}; do
    python simulation.py --minpts=10 --maxpts=1000 --interval=50 --batch=50 --numrunsper=50 --randtype="${type}"
    python read_simul_data.py --randtype="${type}"
done
