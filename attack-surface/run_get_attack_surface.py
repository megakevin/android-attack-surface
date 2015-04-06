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
    work_path = "downloads/"
    apps_info = get_apks_info()

    for app in apps_info:
        subprocess.call(["python2", "apk-download/get_apk.py", "-a", app['apk_name'], "-o", work_path])
        get_callgraph(os.path.join(work_path, app['apk_name'] + ".apk"), work_path)
        measure_attack_surface(os.path.join(work_path, app['apk_name'] + ".apk.cg.txt"))

        # update_apk_info(app['id'])


def get_apks_info():
    apkinfo_select_stmt = '''SELECT id, apkname
                             FROM apkinformation
                             WHERE isdownloaded = FALSE limit 5;'''

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

if __name__ == '__main__':
    main()
