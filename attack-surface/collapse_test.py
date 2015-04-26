__author__ = 'kevin'

import argparse
import os
import psycopg2
from connection import PostgreSQL

from attacksurfacemeter.android_call_graph import AndroidCallGraph
from attacksurfacemeter.loaders.javacg_loader import JavaCGLoader
from attacksurfacemeter.formatters.pgsql_formatter import PgsqlFormatter


def main():
    args = parse_args()
    callgraph_files_location = args.path_to_callgraph_files
    callgraph_file_extension = '.apk.cg.txt'

    apps_info = get_apks_info()

    for app in apps_info:
        callgraph_file = os.path.join(callgraph_files_location, app['apk_name'] + callgraph_file_extension)

        if os.path.exists(callgraph_file):
            print("Loading call graph...")
            g = AndroidCallGraph.from_loader(JavaCGLoader(callgraph_file, []))

            original_node_count = len(g.nodes)
            original_edge_count = len(g.edges)

            print("Collapsing black listed edges...")
            g.collapse_android_black_listed_edges()

            collapsed_node_count = len(g.nodes)
            collapsed_edge_count = len(g.edges)

            print("Updating database for: " + app['apk_name'])
            print(app['apk_name'] + " " + str(original_node_count) + " " + str(original_edge_count) + " " + str(collapsed_node_count) + " " + str(collapsed_edge_count))

            # insert(app['apk_name'],
            #        original_node_count, original_edge_count,
            #        collapsed_node_count, collapsed_edge_count)


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

    parser.add_argument("path_to_callgraph_files",
                        help="The path where the call graph files generated using java-callgraph are located.")

    return parser.parse_args()


def get_apks_info():
    apkinfo_select_stmt = '''SELECT id, apkname
                             FROM apkinformation
                             WHERE isjavaanalyze = FALSE
                             AND isdownloaded = TRUE
                             AND lowerdownloads > 1000 and id = 34500;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(apkinfo_select_stmt)
    apps = c.fetchall()

    apps = [{'id': a[0],
             'apk_name': a[1]}
            for a in apps]

    c.close()
    db.close()

    return apps


def insert(apk_name, original_node_count, original_edge_count, collapsed_node_count, collapsed_edge_count):
    collapse_data_insert_stmt = '''INSERT INTO collapse_data(apk_name,
                                   original_node_count, original_edge_count,
                                   collapsed_node_count, collapsed_edge_count)
                                   VALUES (%s, %s, %s, %s, %s);'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(collapse_data_insert_stmt, (apk_name, original_node_count, original_edge_count,
                                          collapsed_node_count, collapsed_edge_count))

    db.commit()
    c.close()
    db.close()


if __name__ == '__main__':
    main()
