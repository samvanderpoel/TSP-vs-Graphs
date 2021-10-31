#!/bin/bash

# minpts:               smallest point cloud size
# maxpts:               largest point cloud size
# interval:             spacing between point cloud sizes
# numrunsper:           number of point clouds per point cloud size
# batch:                number of point clouds to simulate/test concurrently
# cloudtypes:           point cloud types (mostly probability distributions) to sample from
#                       options are: 
#                           pts_uni         pts_annulus     pts_annulus_random  pts_ball 
#                           pts_corners     pts_normal      pts_spokes          pts_clusnorm
#                           pts_grid        pts_cubediam    pts_concentric_circular_points
# tour, path, bito:     which comparisons to make between graphs
# anoms:                anomalies to check for and record
# par:                  true/false, should cloudtypes be simulated concurrently
# concurrently:         if par is true, how many to simulate concurrently

minpts=10
maxpts=90
interval=10
numrunsper=20
batch=20
cloudtypes=( pts_uni pts_annulus_random pts_ball pts_clusnorm pts_corners pts_normal pts_spokes )
tour="{'tour':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del','bito','path'],"
path="'path':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del'],"
bito="'bito':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del']}"
comps=$tour$path$bito
anoms="{'tour_2del':'<1','path_2del':'<1','path_mst':'==1'}"
par=false
concurrently=2

mkdir tour-wds
mkdir path-wds

if [ $par = true ] ; then
    if test -f sim/args.txt; then
        rm sim/args.txt
    fi
    for type in ${cloudtypes[@]}; do
        a="python sim/main.py --minpts=$minpts --maxpts=$maxpts "
        b="--interval=$interval --numrunsper=$numrunsper --batch=$batch "
        c="--randtype=$type --comps=\"$comps\" --anoms=\"$anoms\""
        echo $a$b$c >> sim/args.txt
    done
    parallel -j $concurrently < sim/args.txt &>/dev/null
    rm sim/args.txt
    for type in ${cloudtypes[@]}; do
        echo "python sim/read_simul_data.py --randtype=${type}" >> sim/args.txt
    done
    parallel -j ${#cloudtypes[@]} < sim/args.txt
    rm sim/args.txt
elif [ $par = false ] ; then
    for type in ${cloudtypes[@]}; do
        python sim/main.py --minpts=$minpts --maxpts=$maxpts --interval=$interval \
            --numrunsper=$numrunsper --batch=$batch --randtype="$type" \
            --comps=${comps} --anoms=${anoms}
        python sim/read_simul_data.py --randtype="${type}"
    done
fi

rm -r tour-wds
rm -r path-wds
