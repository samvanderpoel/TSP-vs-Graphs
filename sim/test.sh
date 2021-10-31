#!/bin/bash

tour="{'tour':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del','bito','path'],"
path="'path':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del'],"
bito="'bito':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del']}"
comps=$tour$path$bito
anoms="{}"

mkdir tour-wds
mkdir path-wds

python sim/main.py --minpts=10 --maxpts=60 --interval=10 --numrunsper=20 --batch=20 --cloudtype=uniform-sqr --comps=${comps} --anoms=${anoms}
python sim/plot_simul_data.py --cloudtype=uniform-sqr

rm -r tour-wds
rm -r path-wds
