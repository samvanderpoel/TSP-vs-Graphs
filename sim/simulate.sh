#!/bin/bash

# jobname:              a unique name identifying the current job
# minpts:               smallest point cloud size
# maxpts:               largest point cloud size
# interval:             spacing between point cloud sizes
# numrunsper:           number of point clouds per point cloud size
# batch:                number of point clouds to simulate/test concurrently
# cloudtypes:           point cloud types (mostly probability distributions) to sample from
#                       options are: 
#                           uniform-sqr     annulus         annulus-rand    uniform-ball 
#                           corners         normal-bivar    spokes          normal-clust
#                           uniform-grid    uniform-diam    concen-circ
# tour, path, bito:     which comparisons to make between graphs
# anoms:                anomalies to check for and record
# par:                  true/false, should cloudtypes be simulated concurrently
# concurrently:         if par is true, how many to simulate concurrently

# SET SIMULATION PARAMETERS HERE:
####################################################################
jobname=job0
minpts=10
maxpts=70
interval=10
numrunsper=50
batch=25
cloudtypes=( uniform-sqr annulus-rand uniform-ball normal-clust corners normal-bivar spokes )
tour="{'tour':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del','bito','path'],"
path="'path':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del'],"
bito="'bito':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del']}"
comps=$tour$path$bito
anoms="{}"
par=true
concurrently=2
####################################################################


mkdir tour-wds
mkdir path-wds

if [ $par = true ] ; then
    if test -f sim/args.txt; then
        rm sim/args.txt
    fi
    for type in ${cloudtypes[@]}; do
        a="python sim/main.py --jobname=\"$jobname\" --minpts=$minpts --maxpts=$maxpts "
        b="--interval=$interval --numrunsper=$numrunsper --batch=$batch "
        c="--cloudtype=$type --comps=\"$comps\" --anoms=\"$anoms\""
        echo $a$b$c >> sim/args.txt
    done
    parallel -j $concurrently < sim/args.txt &>/dev/null
    rm sim/args.txt
    for type in ${cloudtypes[@]}; do
        d="python sim/plot_simul_data.py --jobname=\"$jobname\" "
        e="--cloudtype=${type} --comps=${comps} --subdir=\"\""
        echo $d$e >> sim/args.txt
    done
    parallel -j ${#cloudtypes[@]} < sim/args.txt
    rm sim/args.txt
elif [ $par = false ] ; then
    for type in ${cloudtypes[@]}; do
        python sim/main.py --jobname=$jobname --minpts=$minpts --maxpts=$maxpts \
            --interval=$interval --numrunsper=$numrunsper --batch=$batch \
            --cloudtype="$type" --comps=${comps} --anoms=${anoms}
        python sim/plot_simul_data.py --jobname=$jobname --cloudtype="${type}" \
            --comps=${comps} --subdir=""
    done
fi

rm -r tour-wds
rm -r path-wds
