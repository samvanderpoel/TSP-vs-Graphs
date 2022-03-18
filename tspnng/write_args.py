import argparse
import itertools as it
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--update", dest="update", action="store_true")
    parser.set_defaults(update=False)
    n = parser.parse_args().n
    p = parser.parse_args().p
    q = parser.parse_args().q
    update = parser.parse_args().update

    incomplete = []
    if update:
        top_dirname = f"tour-reports-{n}"
        if os.path.exists(top_dirname):
            for gnuproc in range((n-3)**p):
                gnuprocdir = os.path.join(top_dirname, f"gnuproc{gnuproc}")
                if not os.path.exists(gnuprocdir):
                    incomplete.append(gnuproc)
                elif "success.txt" not in os.listdir(gnuprocdir):
                    incomplete.append(gnuproc)
                elif "failed.txt" in os.listdir(gnuprocdir):
                    print(f"gnuproc {gnuproc} failed")
        else:
            for gnuproc in range((n-3)**p):
                incomplete.append(gnuproc)

    mid_inds = list(range(n-(p+q), n-q))
    mids = [
        list(set(range(n)) - set([(i-1)%n, i, (i+1)%n]))
        for i in mid_inds
    ]

    with open(f"args{n}.txt", "w") as f:
        for idx, mid in enumerate(it.product(*mids)):
            if update and idx not in incomplete:
                continue
            f.write(
                "python main.py"
                + f" --mid=\"{list(mid)}\""
                + f" --n={n}"
                + f" --p={p}"
                + f" --q={q}"
                + f" --gnuproc={idx}\n"
            )
