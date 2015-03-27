__author__ = 'kevin'

import argparse
import subprocess
import os


def main():

    args = parse_args()
    get_callgraph(args.apk, args.output)


def get_callgraph(path_to_apk, output_path):
    # jar xvf [APK FILE] classes.dex
    # dex2jar-0.0.9.15/dex2jar.sh classes.dex
    # java -jar javacg-0.1-SNAPSHOT-static.jar output/classes_dex2jar.jar > javacg.txt

    apk_name = os.path.basename(path_to_apk)

    # Create the dex file from the APK
    subprocess.call(["jar", "xvf", path_to_apk, "classes.dex"])

    # Move the dex file into the output folder
    subprocess.call(["mv", "classes.dex",
                     os.path.join(output_path, apk_name + ".dex")])

    # Create the jar from dex file
    subprocess.call(["dex2jar-0.0.9.15/d2j-dex2jar.sh",
                     os.path.join(output_path, apk_name + ".dex")])

    # Move the jar file into the output folder
    subprocess.call(["mv", apk_name + "-dex2jar.jar",
                     os.path.join(output_path, apk_name + "-dex2jar.jar")])

    # Obtain call graph from jar
    subprocess.call(["java", "-jar", "java-callgraph/javacg-0.1-SNAPSHOT-static.jar",
                     os.path.join(output_path, apk_name + "-dex2jar.jar")],
                    stdout=open(os.path.join(output_path, apk_name + ".cg.txt"), "w"))

def parse_args():

    parser = argparse.ArgumentParser(
        description="Analyzes a software's source code and reports various metrics related to it's attack surface.")

    parser.add_argument("-a", "--apk",
                        help="The apk of the application from which to extract the call graph.")

    parser.add_argument("-o", "--output",
                        help="The folder to output the call graph.")

    return parser.parse_args()


if __name__ == '__main__':
    main()
