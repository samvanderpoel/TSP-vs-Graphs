import argparse
import os


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    n = parser.parse_args().n
    p = parser.parse_args().p

    dirname = f"tour-reports-{n}"
    if os.path.exists(dirname):

        lines_out = {}
        for gnuproc in range((n-3)**p):
            gnuprocdir = os.path.join(dirname, f"gnuproc{gnuproc}")
            if not os.path.exists(gnuprocdir):
                lines_out[gnuproc] = [
                    f"gnuproc {gnuproc}\t\thas not started",
                    "incomplete"
                ]
            elif "failed.txt" in os.listdir(gnuprocdir):
                fname = os.path.join(gnuprocdir, "failed.txt")
                message = open(fname).readlines()[0]
                lines_out[gnuproc] = [message, "failed"]
            elif "success.txt" in os.listdir(gnuprocdir):
                fname = os.path.join(gnuprocdir, "success.txt")
                message = open(fname).readlines()[0]
                lines_out[gnuproc] = [message, "success"]
            else:
                lines_out[gnuproc] = [
                    f"gnuproc {gnuproc}\t\tis incomplete",
                    "incomplete"
                ]

        for gnuproc in sorted(lines_out):
            print(lines_out[gnuproc][0])

        results = [lines_out[gnuproc][1] for gnuproc in lines_out]
        if "failed" in results:
            outcome = "False"
        elif "failed" not in results and "incomplete" in results:
            outcome = "Inconclusive"
        else:
            outcome = "True"
        print(f"\n{outcome}\n")
    else:
        print(f"path {dirname} does not exist")
