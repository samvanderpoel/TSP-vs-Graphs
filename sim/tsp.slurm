#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/TSP-vs-Graphs
#SBATCH --job-name=tsp
#SBATCH --output=sim/tspout.txt
#SBATCH --time=2-00:00:00
#SBATCH --partition=long-28core
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load gnu-parallel
module load anaconda/3
source activate tsp

minpts=1510
maxpts=1560
interval=50
numrunsper=50
batch=50
cloudtypes=( uniform-sqr annulus-rand uniform-ball normal-clust corners normal-bivar spokes )
tour="{'tour':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del','bito','path'],"
path="'path':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del'],"
bito="'bito':['1nng','2nng','20pt','mst','gab','urq','del','1del','2del']}"
comps=$tour$path$bito
anoms="{}"
par=true
concurrently=7

mkdir tour-wds
mkdir path-wds

if [ $par = true ] ; then
    if test -f sim/args.txt; then
        rm sim/args.txt
    fi
    for type in ${cloudtypes[@]}; do
        a="python sim/main.py --minpts=$minpts --maxpts=$maxpts "
        b="--interval=$interval --numrunsper=$numrunsper --batch=$batch "
        c="--cloudtype=$type --comps=\"$comps\" --anoms=\"$anoms\""
        echo $a$b$c >> sim/args.txt
    done
    parallel -j $concurrently < sim/args.txt &>/dev/null
    rm sim/args.txt
    for type in ${cloudtypes[@]}; do
        echo "python sim/plot_simul_data.py --cloudtype=${type}" >> sim/args.txt
    done
    parallel -j ${#cloudtypes[@]} < sim/args.txt
    rm sim/args.txt
elif [ $par = false ] ; then
    for type in ${cloudtypes[@]}; do
        python sim/main.py --minpts=$minpts --maxpts=$maxpts --interval=$interval \
            --numrunsper=$numrunsper --batch=$batch --cloudtype="$type" \
            --comps=${comps} --anoms=${anoms}
        python sim/plot_simul_data.py --cloudtype="${type}"
    done
fi

rm -r tour-wds
rm -r path-wds
