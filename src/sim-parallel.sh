#!/bin/bash

PT_CLOUD_TYPES=( pts_uni pts_annulus_random pts_ball pts_clusnorm pts_corners pts_normal pts_spokes )
#PT_CLOUD_TYPES=( pts_uni pts_annulus_random )

minpts=10
maxpts=110
interval=50
numrunsper=15
batch=15

mkdir tour-wds
mkdir path-wds

for type in ${PT_CLOUD_TYPES[@]}; do
    echo "python src/main.py --minpts=${minpts} --maxpts=${maxpts} --interval=${interval} \
    --numrunsper=${numrunsper} --batch=${batch} --randtype=${type}" >> src/args.txt
done

parallel -j $((${#PT_CLOUD_TYPES[@]}+1)) < src/args.txt
rm src/args.txt
rm -r tour-wds
rm -r path-wds

for type in ${PT_CLOUD_TYPES[@]}; do
    echo "python src/read_simul_data.py --randtype=${type}" >> src/args.txt
done

parallel -j $((${#PT_CLOUD_TYPES[@]}+1)) < src/args.txt
rm src/args.txt
