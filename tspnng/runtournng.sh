#!/bin/bash

n=13
p=2 # gnu-parallel will spawn (n-3)^p tasks
q=2 # each task spawned by gnu-parallel will spawn (n-3)^q subprocesses

mkdir tour-reports-${n}
python write_args.py --n ${n} --p ${p} --q ${q} --update
parallel -j 2 --halt now,fail=1 < args${n}.txt
rm args${n}.txt
python report.py --n ${n} --p ${p} > result${n}.txt
