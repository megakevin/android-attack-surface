__author__ = 'kevin'

import argparse
import os
import subprocess

import psycopg2
from connection import PostgreSQL

from android_callgraph.get_callgraph import get_callgraph

from attacksurfacemeter.call_graph import CallGraph
from attacksurfacemeter.loaders.javacg_loader import JavaCGLoader
from attacksurfacemeter.formatters.pgsql_formatter import PgsqlFormatter


def main():
    args = parse_args()
    work_path = args.output_path

    apps_info = get_apks_info()

    for app in apps_info:
        print("Downloading apk for: " + app['apk_name'])
        subprocess.call([args.python2_exe,
                         "apk_download/get_apk.py",
                         "-a", app['apk_name'], "-o", work_path])

        print("Generating call graph for: " + app['apk_name'])
        get_callgraph(os.path.join(work_path, app['apk_name'] + ".apk"), work_path)

        # print("Measuring attack surface for: " + app['apk_name'])
        # measure_attack_surface(os.path.join(work_path, app['apk_name'] + ".apk.cg.txt"))

        update_apk_info(app['id'])

        clean_up(work_path, app['apk_name'])

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

    parser.add_argument("-p", "--python2_exe",
                        help="The Python 2 executable with which to run the apk downloader.")

    parser.add_argument("-o", "--output_path",
                        help="The path to save the downloaded apks and generated call graph files.")

    return parser.parse_args()


def get_apks_info():
    apkinfo_select_stmt = '''SELECT id, apkname
                             FROM apkinformation
                             WHERE isdownloaded = FALSE;'''

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


def measure_attack_surface(input_call_graph_file):
    g = CallGraph.from_loader(JavaCGLoader(input_call_graph_file))
    g.collapse_android_black_listed_packages()

    f = PgsqlFormatter(g, PostgreSQL.connection_string)
    f.write_output()


def update_apk_info(apk_info_id):
    apkinfo_update_stmt = '''UPDATE apkinformation
                             SET isdownloaded = TRUE
                             WHERE id = %s;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(apkinfo_update_stmt, (apk_info_id,))

    db.commit()
    c.close()
    db.close()


def clean_up(work_path, apk_name):
    os.remove(os.path.join(work_path, apk_name + ".apk"))
    os.remove(os.path.join(work_path, apk_name + ".apk.dex"))
    os.remove(os.path.join(work_path, apk_name + ".apk-dex2jar.jar"))

if __name__ == '__main__':
    main()
