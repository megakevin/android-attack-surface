__author__ = 'kevin'

import argparse
import os
import psycopg2
from connection import PostgreSQL

from get_attack_surface import get_attack_surface


def main():
    args = parse_args()
    callgraph_files_location = args.path_to_callgraph_files
    callgraph_file_extension = '.apk.cg.txt'

    apps_info = get_apks_info()

    for app in apps_info:
        callgraph_file = os.path.join(callgraph_files_location, app['apk_name'] + callgraph_file_extension)

        if os.path.exists(callgraph_file) and os.path.getsize(callgraph_file) < 10000000 and os.path.getsize(callgraph_file) > 0:
            print("Calculating attack surface for: " + app['apk_name'])
            get_attack_surface(callgraph_file)

            print("Updating database for: " + app['apk_name'])
            update_attack_surface(app['apk_name'], callgraph_file)
            update_apk_info(app['id'])
        else:
            print("Skipping: " + app['apk_name'])


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
                             AND lowerdownloads > 1000
                             ORDER BY id DESC;'''

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


def update_attack_surface(new_attack_surface_source, old_attack_surface_source):
    attack_surface_update_stmt = '''UPDATE attack_surfaces
                                    SET source = %s
                                    WHERE source = %s;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(attack_surface_update_stmt, (new_attack_surface_source, old_attack_surface_source))

    db.commit()
    c.close()
    db.close()


def update_apk_info(apk_info_id):
    apkinfo_update_stmt = '''UPDATE apkinformation
                             SET isjavaanalyze = TRUE
                             WHERE id = %s;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(apkinfo_update_stmt, (apk_info_id,))

    db.commit()
    c.close()
    db.close()


if __name__ == '__main__':
    main()
