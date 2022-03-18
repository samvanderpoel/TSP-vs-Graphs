#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/TSP-vs-Graphs/tspnng
#SBATCH --job-name=tspnng13
#SBATCH --output=/dev/null
#SBATCH --time=0-12:00:00
#SBATCH --partition=medium-28core
#SBATCH --nodes=24
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load gnu-parallel
module load anaconda/3
source activate tsp

n=13
p=3 # gnu-parallel will spawn (n-3)^p tasks
q=3 # each task spawned by gnu-parallel will spawn (n-3)^q subprocesses

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q} --update
parallel -j24 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
