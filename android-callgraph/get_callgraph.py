__author__ = 'kevin'

import argparse
import subprocess


def main():

    args = parse_args()

    # jar xvf [APK FILE] classes.dex
    # dex2jar-0.0.9.15/dex2jar.sh classes.dex
    # java -jar javacg-0.1-SNAPSHOT-static.jar output/classes_dex2jar.jar > javacg.txt

    # Create the dex file from the APK
    subprocess.call(["jar", "xvf", "input/" + args.apk, "classes.dex"])

    # Move the dex file into the output folder
    subprocess.call(["mv", "classes.dex", "output/" + args.apk + ".dex"])

    # Create the jar from dex file
    subprocess.call(["dex2jar-0.0.9.15/dex2jar.sh", "output/" + args.apk + ".dex"])

    # Obtain call graph from jar
    subprocess.call(["java", "-jar", "java-callgraph/javacg-0.1-SNAPSHOT-static.jar",
                     "output/" + args.apk + "_dex2jar.jar"],
                    stdout=open("output/" + args.apk + ".cg.txt", "w"))


def parse_args():

    parser = argparse.ArgumentParser(
        description="Analyzes a software's source code and reports various metrics related to it's attack surface.")

    parser.add_argument("-apk", "--apk",
                        help="The apk of the application from which to extract the call graph.")

    return parser.parse_args()


if __name__ == '__main__':
    main()
