#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/Simulate-TSP/tspnng-checker
#SBATCH --partition=extended-40core
#SBATCH --job-name=tspnng
#SBATCH --output=stdout.txt
#SBATCH --time=7-00:00:00
#SBATCH --ntasks-per-node=40
#SBATCH --nodes=2
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load shared
module load anaconda/3
source activate tsp

python tournng.py --n 10 --p 4
