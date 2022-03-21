#!/bin/bash

n=9
p=3 # gnu-parallel will spawn (n-3)^p tasks
q=3 # each task spawned by gnu-parallel will spawn (n-3)^q subprocesses

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q} --update
parallel -j4 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
