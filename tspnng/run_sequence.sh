#!/bin/bash

module load anaconda/3

n=12
p=3 # gnu-parallel will spawn (n-3)^p tasks
q=3 # each gnu-parallel task will spawn (n-3)^q processes

for (( i=0; i>=0; i++ )); do
    echo "WORKING ON ITERATION ${i}"
    sbatch --wait run_tour_nng.slurm ${n} ${p} ${q}
    rm -f args${n}.txt
    python report.py --n ${n} --p ${p} > results${n}.txt
    results=$(cat results${n}.txt)
    [[ $results == *"Inconclusive"* ]] || break
done
