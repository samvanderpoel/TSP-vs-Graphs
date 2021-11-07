#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/tspnng-checker
#SBATCH --partition=long-40core
#SBATCH --job-name=tspnng9
#SBATCH --output=out9.txt
#SBATCH --time=2-00:00:00
#SBATCH --nodes=6
#SBATCH --cpus-per-task=40
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load shared
module load anaconda/3
source activate tsp

python tournng.py --n 9 --p 4
