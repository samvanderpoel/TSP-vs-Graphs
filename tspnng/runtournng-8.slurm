#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/tspnng-checker
#SBATCH --partition=short-24core
#SBATCH --job-name=tspnng8
#SBATCH --output=out8.txt
#SBATCH --time=0-04:00:00
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load shared
module load anaconda/3
source activate tsp

python tournng.py --n 8 --p 3
