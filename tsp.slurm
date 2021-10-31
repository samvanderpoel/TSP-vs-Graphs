#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/SimulateTSP
#SBATCH --partition=extended-28core
#SBATCH --job-name=tsp
#SBATCH --output=stdout.txt
#SBATCH --time=7-00:00:00
#SBATCH --ntasks-per-node=28
#SBATCH --nodes=2
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load shared
module load gnu-parallel
module load anaconda/3
source activate tsp

bash sim/simulate.sh
