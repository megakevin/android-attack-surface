__author__ = 'kevin'

import time
import psycopg2

from connection import PostgreSQL
from get_reviews import get_reviews


def main():
    apps_info = get_apps_info()

    for app in apps_info:
        print("Downloading reviews for " + app['apk_name'] + " - Id: " + str(app['id']))
        get_reviews(app['apk_name'], app['number_of_reviews'])
        print("Updating isreviewsdownloaded flag on " + app['apk_name'] + " - Id: " + str(app['id']))
        update_app(app['id'])

        print("Sleeping 30...")
        time.sleep(30)

    print("Exiting...")


def get_apps_info():
    apkinfo_select_stmt = '''SELECT id, apkname, numberofreviews
                             FROM apkinformation
                             WHERE isreviewsdownloaded = FALSE
                             AND isdownloaded = TRUE
                             AND lowerdownloads > 1000;'''

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
