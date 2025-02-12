import sys
filename = sys.argv[1]
with open(filename) as f:
    for i in f:
        i = i.replace("\n", "")
        x = i.split()
        print(f"{x[0]}\t{1}")