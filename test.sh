#!/bin/bash

tour="{'tour':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del','bito','path'],"
path="'path':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del'],"
bito="'bito':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del']}"
comps=$tour$path$bito
anoms="{}"

mkdir tour-wds
mkdir path-wds

python src/main.py --minpts=10 --maxpts=60 --interval=10 --numrunsper=20 --batch=20 --randtype=pts_uni --comps=${comps} --anoms=${anoms}
python src/read_simul_data.py --randtype=pts_uni

rm -r tour-wds
rm -r path-wds
