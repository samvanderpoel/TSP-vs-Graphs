#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/Simulate-TSP/tspnng-checker
#SBATCH --partition=large-40core
#SBATCH --job-name=tspnng10
#SBATCH --output=out10.txt
#SBATCH --time=0-08:00:00
#SBATCH --ntasks-per-node=40
#SBATCH --nodes=50
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load shared
module load anaconda/3
module load gnu-parallel
source activate tsp

python tournng.py --n 10 --p 4
