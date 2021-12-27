#!/bin/bash

jobname=main
cloudtypes=( uniform-sqr annulus-rand uniform-ball normal-clust corners normal-bivar spokes )

tourstd="{'tour':['1nng','2nng','mst','gab','urq','del','path'],"
pathstd="'path':['1nng','2nng','mst','gab','urq','del'],"
bitostd="'bito':['1nng','2nng','mst','gab','urq','del']}"
compstd=$tourstd$pathstd$bitostd

tourgdl="{'tour':['20pt','1del','2del'],"
pathgdl="'path':['20pt','1del','2del']}"
compgdl=$tourgdl$pathgdl

for type in ${cloudtypes[@]}; do
    python sim/plot_simul_data.py --jobname=$jobname --cloudtype="${type}" \
        --comps=${compstd} --subdir="std/"
    python sim/plot_simul_data.py --jobname=$jobname --cloudtype="${type}" \
        --comps=${compgdl} --subdir="gdl/" --mi 210
done
