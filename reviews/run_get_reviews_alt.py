__author__ = 'kevin'

import time
import psycopg2
import os

from connection import PostgreSQL
from get_reviews import get_reviews


def main():
    apps_info = get_apps_info()

    # callgraph_files_location = '../android-callgraph/downloads/'
    callgraph_files_location = '/media/kevin/Data/Documents/call_graphs/'
    callgraph_file_extension = '.apk.cg.txt'

    for app in apps_info:

        callgraph_file = os.path.join(callgraph_files_location, app['apk_name'] + callgraph_file_extension)

        if os.path.exists(callgraph_file) and os.path.getsize(callgraph_file) < 10000000 and os.path.getsize(callgraph_file) > 0:

            print("Downloading reviews for " + app['apk_name'] + " - Id: " + str(app['id']))

            try:
                get_reviews(app['apk_name'], app['number_of_reviews'])
                print("Updating isreviewsdownloaded flag on " + app['apk_name'] + " - Id: " + str(app['id']))
                update_app(app['id'])

                print("Sleeping 20...")
                time.sleep(20)
            except:
                print("Sleeping for 5 minutes...")
                time.sleep(5 * 60)

        else:
            print("Skipping: " + app['apk_name'])

    print("Exiting...")


def get_apps_info():
    apkinfo_select_stmt = '''SELECT id, apkname, numberofreviews
                             FROM apkinformation
                             WHERE isreviewsdownloaded = FALSE
                             AND isdownloaded = TRUE
                             AND lowerdownloads > 1000
                             ORDER BY id DESC;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(apkinfo_select_stmt)
    apps = c.fetchall()

    apps = [{'id': a[0],
             'apk_name': a[1],
             'number_of_reviews': a[2]}
            for a in apps]

    c.close()
    db.close()

    return apps


def update_app(apk_info_id):
    apkinfo_update_stmt = '''UPDATE apkinformation
                             SET isreviewsdownloaded = TRUE
                             WHERE id = %s;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(apkinfo_update_stmt, (apk_info_id,))

    db.commit()
    c.close()
    db.close()


if __name__ == '__main__':
    main()
