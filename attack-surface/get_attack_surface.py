__author__ = 'kevin'

import argparse

from connection import PostgreSQL

from attacksurfacemeter.android_call_graph import AndroidCallGraph
from attacksurfacemeter.loaders.javacg_loader import JavaCGLoader
from attacksurfacemeter.formatters.pgsql_formatter import PgsqlFormatter
# from attacksurfacemeter.formatters.sqlite_formatter import SqliteFormatter


def main():
    args = parse_args()
    get_attack_surface(args.callgraph)


def parse_args():
    """
        Provides a command line interface.

        Defines all the positional and optional arguments along with their respective valid values
        for the command line interface and returns all the received arguments as an object.

        Returns:
            An object that contains all the provided command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Downloads the specified APK from the google play store.")

    parser.add_argument("callgraph",
                        help="The file containing java-callgraph's output for an android app.")

    return parser.parse_args()


def get_attack_surface(callgraph_file):
    print("Loading call graph...")
    g = AndroidCallGraph.from_loader(JavaCGLoader(callgraph_file, []))

    print("Collapsing black listed edges...")
    g.collapse_android_black_listed_edges()

    print("Calculating entry and exit points...")
    g.calculate_entry_and_exit_points()

    print("Calculating attack surface nodes...")
    g.calculate_attack_surface_nodes()

    print("Writing to database...")
    f = PgsqlFormatter(g, PostgreSQL.connection_string)
    # f = SqliteFormatter(g, 'demo.db')
    # If the data base didn't exist we would run this
    # f.init_database()
    f.write_output()


if __name__ == '__main__':
    main()
