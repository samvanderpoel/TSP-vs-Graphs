#!/bin/bash
#
#SBATCH --partition=extended-28core
#SBATCH --job-name=tsp
#SBATCH --output=res.txt
#SBATCH --time=6-23:59:59
#SBATCH --ntasks-per-node=28
#SBATCH --nodes=2

module load shared
module load anaconda/3

bash src/simulate.sh
