__author__ = 'kevin'

import argparse
import os
from get_callgraph import get_callgraph


def main():
    args = parse_args()

    apks = [os.path.join(args.input_path, f) for f in os.listdir(args.input_path)
            if os.path.isfile(os.path.join(args.input_path, f))
            and os.path.splitext(f)[1]]

    for apk in apks:
        # print(apk)
        get_callgraph(apk, args.output_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyzes a software's source code and reports various metrics related to it's attack surface.")

    parser.add_argument("-i", "--input_path",
                        help="The path from where to get the apks from which to extract the call graphs.")

    parser.add_argument("-o", "--output_path",
                        help="The folder to output the call graphs.")

    return parser.parse_args()


if __name__ == '__main__':
    main()
