#!/bin/bash

# jobname:       a unique name identifying the current job
# cloudtypes:    point cloud types (mostly prob distributions)
#                to sample from. options are: 
#                    uniform-sqr     annulus
#                    annulus-rand    uniform-ball 
#                    corners         normal-bivar
#                    spokes          normal-clust
#                    uniform-grid    uniform-diam
#                    concen-circ
# par:           true/false, should cloudtypes be simulated
#                concurrently
# concurrently:  if par is true, how many to simulate
#                concurrently

jobname=test
config_simul=sim/config_simul/${jobname}.yaml
config_plots=sim/config_plots/${jobname}.yaml
cloudtypes=( uniform-sqr annulus-rand )
par=false
concurrently=2

mkdir tour-wds
mkdir path-wds

if [ $par = true ] ; then
    if test -f sim/args.txt; then
        rm sim/args.txt
    fi
    for type in ${cloudtypes[@]}; do
        args="--config $config_simul --cloudtype $type"
        echo "python sim/main.py $args" >> sim/args.txt
    done
    parallel -j $concurrently < sim/args.txt &>/dev/null
    rm sim/args.txt
elif [ $par = false ] ; then
    for type in ${cloudtypes[@]}; do
        python sim/main.py --config $config_simul --cloudtype $type
    done
fi

rm -r tour-wds
rm -r path-wds

for type in ${cloudtypes[@]}; do
    python sim/plot_data.py --config $config_plots --cloudtype $type
done
