import os

# delete all items in cwd that are not .py, .sh, .slurm, .txt, or directory
cwd = os.getcwd()
contents = os.listdir(cwd)
for item in contents:
    if not item.endswith(".py") and not item.endswith(".sh") and \
       not item.endswith(".slurm") and not item.endswith(".txt") and \
       not os.path.isdir(os.path.join(cwd, item)):
        os.remove(os.path.join(cwd, item))
    if "tour-wd" in item or "path-wd" in item:
        os.rmdir(os.path.join(cwd, item))
if os.path.isdir(os.path.join(cwd, "__pycache__")):
    os.system("rm -r __pycache__")
