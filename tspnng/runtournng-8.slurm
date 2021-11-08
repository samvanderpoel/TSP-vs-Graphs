#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/tspnng
#SBATCH --job-name=tspnng8
#SBATCH --output=/dev/null
#SBATCH --time=0-04:00:00
#SBATCH --partition=short-24core
#SBATCH --nodes=5
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load anaconda/3
module load gnu-parallel
source activate tsp

n=8
p=2
q=3

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q}
parallel -j 5 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
