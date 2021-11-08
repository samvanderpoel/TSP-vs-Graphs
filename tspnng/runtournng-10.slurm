#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/tspnng
#SBATCH --job-name=tspnng10
#SBATCH --output=/dev/null
#SBATCH --time=0-08:00:00
#SBATCH --partition=large-40core
#SBATCH --nodes=50
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load anaconda/3
module load gnu-parallel
source activate tsp

n=10
p=3
q=3

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q}
parallel -j 50 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
