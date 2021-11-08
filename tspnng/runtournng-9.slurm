#!/bin/bash
#
#SBATCH -D/gpfs/scratch/svanderpoel/tspnng
#SBATCH --job-name=tspnng9
#SBATCH --output=/dev/null
#SBATCH --time=0-12:00:00
#SBATCH --partition=medium-40core
#SBATCH --nodes=16
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=sam.vanderpoel@stonybrook.edu

module load anaconda/3
module load gnu-parallel
source activate tsp

n=9
p=2
q=3

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q}
parallel -j 16 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
