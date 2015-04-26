__author__ = 'kevin'

import argparse
import os
import psycopg2
from connection import PostgreSQL


def main():
    args = parse_args()

    callgraph_files_location = args.path_to_callgraph_files
    callgraph_file_extension = '.apk.cg.txt'
    done_dir_name = "done"

    apps_info = get_apks_info()

    for app in apps_info:
        file_name = os.path.join(callgraph_files_location, app['apk_name'] + callgraph_file_extension)
        new_file_name = os.path.join(callgraph_files_location, done_dir_name, app['apk_name'] + callgraph_file_extension)

        if os.path.exists(file_name):
            print("Moving " + file_name + " to " + new_file_name)
            os.rename(file_name, new_file_name)


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
                             WHERE isjavaanalyze = TRUE;'''

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


if __name__ == '__main__':
    main()
