#!/bin/bash

jobname=main
config_plots=sim/config_plots/${jobname}.yaml
cloudtypes=( uniform-sqr annulus-rand uniform-ball normal-clust corners normal-bivar spokes )

for type in ${cloudtypes[@]}; do
    python sim/plot_simul_data.py --config $config_plots --cloudtype $type
done
