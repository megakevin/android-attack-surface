__author__ = 'kevin'

import argparse
import sqlite3
import networkx as nx


def main():

    args = parse_args()
    call_graph = nx.DiGraph()

    with open(args.javacgfile) as raw_call_graph:
        # line is like this:
        # M:com.example.kevin.helloandroid.Greeter:sayHelloInSpanish (M)java.lang.StringBuilder:toString.
        for line in raw_call_graph:
            if line.startswith("M:"):
                caller, callee = line.split(" ")

                caller = caller[2:].strip()  # Remove the trailing "M:"
                callee = callee[3:].strip()  # Remove the trailing "(*)"

                call_graph.add_edge(caller, callee)

    edges_to_insert = []

    for edge in call_graph.edges():
        caller, callee = edge
        caller_package, caller_class = get_decomposed_name(caller)
        callee_package, callee_class = get_decomposed_name(callee)

        edges_to_insert.append((caller, caller_package, caller_class,
                                callee, callee_package, callee_class,
                                args.application))

    print("call graph file loaded into memory")

    with sqlite3.connect('android.cg.db') as db:
        db.executemany('INSERT INTO edges ('
                       'caller, caller_package, caller_class, '
                       'callee, callee_package, callee_class, '
                       'app) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?)', edges_to_insert)

    print("call graph loaded into database")


def get_decomposed_name(method):
    # return ".".join(method.split(":")[0].split(".")[:-1])

    class_name = method.split(":")[0]

    if "." in class_name:
        package_name = ".".join(class_name.split(".")[:-1])
    else:
        package_name = class_name

    return package_name, class_name


def parse_args():
    """
        Provides a command line interface.

        Defines all the positional and optional arguments along with their respective valid values
        for the command line interface and returns all the received arguments as an object.

        Returns:
            An object that contains all the provided command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes a software's source code and reports various metrics related to it's attack surface.")

    parser.add_argument("-jf", "--javacgfile",
                        help="The file containing java-callgraph's output")

    parser.add_argument("-app", "--application",
                        help="The name of the application from which this callgraph was generated")

    return parser.parse_args()


if __name__ == '__main__':
    main()
