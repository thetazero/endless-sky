from parse import parse
from graph import visualize_missions

if __name__ == "__main__":
    res = parse("../data/human/kestrel.txt")
    res = [mission for mission in res if mission]
    visualize_missions(res, "output.dot")
    print(res)
