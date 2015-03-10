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

    edges_to_insert = [(edge[0], edge[1], args.application) for edge in call_graph.edges()]

    print("call graph file loaded into memory")

    with sqlite3.connect('android.cg.db') as db:
        db.executemany('INSERT INTO edges (caller, callee, app) VALUES (?, ?, ?)', edges_to_insert)

    print("call graph loaded into database")


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
