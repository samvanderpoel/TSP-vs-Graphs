import os
import sys
import argparse
import numpy as np
from termcolor import colored
import csv
import re

parser = argparse.ArgumentParser()
parser.add_argument("--jobname", type=str, required=True)
parser.add_argument("--summary", dest="summary", action="store_true")
parser.add_argument("--all", dest="summary", action="store_false")
parser.add_argument("--export", dest="export", action="store_true")
parser.set_defaults(summary=True, export=False)
args = parser.parse_args()
jobname = args.jobname
summary = args.summary
export = args.export

cwd = os.getcwd()
jobpath = os.path.join(cwd, "results", jobname)
if not os.path.isdir(jobpath):
    print("No data to report")
    sys.exit()
contents = os.listdir(jobpath)

types = [
    "uniform-sqr",
    "annulus",
    "annulus-rand",
    "uniform-ball",
    "normal-clust",
    "uniform-diam",
    "corners",
    "uniform-grid",
    "normal-bivar",
    "spokes",
    "concen-circ",
]
dirnames = [name + "-results" for name in types]
templabs = {
    "20pt": "20% NNG",
    "del": "Delaunay",
    "1del": "Order-1 Delaunay",
    "2del": "Order-2 Delaunay",
    "gab": "Gabriel",
    "tour": "TSP Tour",
    "path": "TSP Path",
    "2nng": "2-NNG",
    "urq": "Urquhart",
    "mst": "MST",
    "dmg": "Delaunay \\ Gabriel",
    "1nng": "1-NNG",
    "bito": "Bitonic TSP",
}
results = [
    [
        "cloud_type",
        "majorid",
        "minorid",
        "minpts",
        "maxpts",
        "min",
        "pct25",
        "median",
        "mean",
        "pct75",
        "max",
        "stddev",
        "subset",
    ]
]

for item in contents:
    itempath = os.path.join(jobpath, item)
    if os.path.isdir(itempath) and item in dirnames:
        try:
            data = eval(open(itempath + "/data.txt", "r").read())
            which_comps = {}
            for comp in data:
                major_id, minor_id = comp.split("_")
                if major_id not in which_comps:
                    which_comps[major_id] = []
                which_comps[major_id] += [minor_id]
            graphs_to_compute = (
                set(which_comps.keys()) |
                set(
                    graphid
                    for v in which_comps.values()
                    for graphid in v
                )
            )
            kdels_labs = {
                g:" ".join(["Order-" + str(g[:-3]), "Delaunay"])
                for g in graphs_to_compute
                if re.match("[0-9]+del", g)
            }
            knngs_labs = {
                g: "".join([str(g[:-3]), "-NNG"])
                for g in graphs_to_compute
                if re.match("[0-9]+nng", g)
            }
            labels = {**templabs, **kdels_labs, **knngs_labs}

            print(colored("\n\n" + item[:-8].upper() + " DATA:", "green"))
            print(colored(55 * "-", "green"))
            for comp, v in data.items():
                majorid, minorid = comp.split("_")
                major_name, minor_name = labels[majorid], labels[minorid]
                print(
                    colored(
                        f"{major_name} vs. {minor_name} comparisons: ",
                        "red"
                    )
                )
                all_data = np.array([
                    frac
                    for _, data in v.items()
                    for frac in data
                ])
                numtot = len(all_data)
                minpts = min([num for num, data in v.items()])
                maxpts = max([num for num, data in v.items()])
                minimum = round(np.percentile(all_data, 0), 3)
                pct25 = round(np.percentile(all_data, 25), 3)
                median = round(np.percentile(all_data, 50), 3)
                ave = round(np.mean(all_data), 3)
                pct75 = round(np.percentile(all_data, 75), 3)
                maximum = round(np.percentile(all_data, 100), 3)
                stdpts = round(np.std(all_data), 3)
                print("min\t25\tmed\tmean\t75\tmax\tstdev")
                print(
                    f"{minimum}\t{pct25}\t{median}\t{ave}\t"
                    f"{pct75}\t{maximum}\t{stdpts}"
                )
                subset = round(np.mean(all_data == 1), 3)
                print(
                    "Total number of point clouds simulated: "
                    + colored(str(numtot), "yellow")
                )
                print(
                    "Range of point cloud sizes: "
                    + colored(f"{minpts} to {maxpts}", "yellow")
                )
                print(
                    "Fraction of point clouds whose intersection is 100%: "
                    + colored(str(subset), "yellow")
                )
                new_result = [
                    item[:-8],
                    majorid,
                    minorid,
                    minpts,
                    maxpts,
                    minimum,
                    pct25,
                    median,
                    ave,
                    pct75,
                    maximum,
                    stdpts,
                    subset,
                ]
                results.append(new_result)
                if not summary:
                    for num, data in v.items():
                        print(
                            f"num pts: {num}\t\t"
                            f"point clouds simulated:\t{len(data)}"
                        )
                print("")
            print(colored("\033[F" + 55*"-", "green"))
        except:
            continue

if export:
    with open(
        os.path.join("results", jobname, "stats.csv"),
        "w",
        newline="\n"
    ) as f:
        writer = csv.writer(f)
        writer.writerows(results)
