#!/bin/bash
#
#SBATCH -D/gpfs/projects/MitchellGroup/TSP-vs-Graphs/tspnng
#SBATCH --job-name=tspnng
#SBATCH --output=/dev/null
#SBATCH --partition=medium-28core
#SBATCH --nodes=24
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=0-12:00:00
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load gnu-parallel
module load anaconda/3
source activate tsp

n=${1}
p=${2} # gnu-parallel will spawn (n-3)^p tasks
q=${3} # each gnu-parallel task will spawn (n-3)^q processes
n_nodes=24

rm -f args${n}.txt
rm -f results${n}.txt
mkdir -p tour-reports-${n}

python write_args.py --n ${n} --p ${p} --q ${q} --update
parallel -j${n_nodes} --halt now,fail=1 < args${n}.txt
