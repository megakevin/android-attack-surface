__author__ = 'kevin'

import urllib.request
import urllib.parse

# Python 2 compatibility
# import urllib2
# import urllib

import json
import re
from xml.dom import minidom
import time
# import sqlite3
import argparse
import datetime
import psycopg2
from connection import PostgreSQL


def main():
    args = parse_args()
    get_reviews(args.application, args.number)


def parse_args():
    """
        Provides a command line interface.

        Defines all the positional and optional arguments along with their respective valid values
        for the command line interface and returns all the received arguments as an object.

        Returns:
            An object that contains all the provided command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Gets all the user reviews on the specified APK and saves it into a database.")

    parser.add_argument("-a", "--application",
                        help="The id of the app to get the reviews from.")

    parser.add_argument("-n", "--number", type=int,
                        help="The number of reviews to request.")

    return parser.parse_args()


def get_reviews(application, number_of_reviews):
    page_size = 40

    # calculate the number of pages to request to obtain the given number of reviews
    # max_pages = int(number_of_reviews / page_size) + 1
    max_pages = 15

    for page_number in range(1, max_pages + 1):

        print("Sleeping 15...")
        time.sleep(15)

        print("Downloading page: " + str(page_number))

        response = make_request(application, page_number)
        print("Reviews request made for: " + application)

        reviews = parse_response(response)
        print("Reviews response parsed for: " + application)

        save_reviews(application, reviews)
        print("Reviews saved into the database for: " + application)

        # distict_reviews = get_number_of_distinct_reviews(application)
        # total_reviews = get_number_of_total_reviews(application)

        # if distict_reviews < total_reviews:
        #     print("Exiting because found repeated reviews!")
        #     print("distict_reviews = " + str(distict_reviews))
        #     print("total_reviews = " + str(total_reviews))
        #     return


def get_number_of_distinct_reviews(app_id):
    reviews_select_stmt = '''with distinct_reviews as (
                                SELECT app_id, title, body, rating
                                FROM reviews
                                where app_id = %s
                                GROUP BY app_id, title, body, rating
                            )
                            select count(*) from distinct_reviews;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(reviews_select_stmt, (app_id,))
    number = c.fetchone()[0]

    c.close()
    db.close()

    return number


def get_number_of_total_reviews(app_id):
    reviews_select_stmt = '''select count(*)
                             from reviews
                             where app_id = %s;'''

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.execute(reviews_select_stmt, (app_id,))
    number = c.fetchone()[0]

    c.close()
    db.close()

    return number

def make_request(application_id, page_number):
    request = urllib.request.Request("https://play.google.com/store/getreviews", method="POST")
    # Python 2 compatibility
    # request = urllib2.Request("https://play.google.com/store/getreviews")

    request.add_header("content-type", "application/x-www-form-urlencoded; charset=utf-8")
    request.add_header("origin", "https://play.google.com")
    request.add_header("cache-control", "no-cache")
    request.add_header("referer", "https://play.google.com/store/apps/details?id=" + application_id)

    request.add_header("referer", "https://play.google.com/store")
    request.add_header("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36")

    request.add_header("x-client-data", "CJW2yQEIpbbJAQiptskBCJ6SygEIrZXKARiricoB")
    request.add_header("x-requested-with", "XMLHttpRequest")

    data = urllib.parse.urlencode({'reviewType': "0",
                                   'pageNum': page_number,
                                   'id': application_id,  # "com.github.mobile"
                                   'reviewSortOrder': "0",
                                   'xhr': "1",
                                   'token': "oCu4PNapSrAMxh2-vqD_iMxod_g:1394178244711"})
    # Python 2 compatibility
    # data = urllib.urlencode({'reviewType': "0",
    #                          'pageNum': page_number,
    #                          'id': application_id,  # "com.github.mobile"
    #                          'reviewSortOrder': "0",
    #                          'xhr': "1",
    #                          'token': "oCu4PNapSrAMxh2-vqD_iMxod_g:1394178244711"})

    data = data.encode('utf-8')

    response = urllib.request.urlopen(request, data)
    # Python 2 compatibility
    # response = urllib2.urlopen(request, data)

    return response


def parse_response(response):
    result = []

    # this is to turn the bytes that come in the response into a python string
    response = str(response.read(), "utf-8")
    # Python 2 compatibility
    # response = str(response.read())

    # apparently random garbage
    response = response.replace(")]}'", " ")

    # this converts the string to json and takes care of all unescaping
    response = json.loads(response)

    # this is where the reviews are
    reviews = response[0][2]

    # deleting all <img> tags because since they don't close, they are not valid xml
    while re.search(r"<img\s[^>]*?src\s*=\s*['\"]([^'\"]*?)['\"][^>]*?>", reviews):
        m = re.search(r"<img\s[^>]*?src\s*=\s*['\"]([^'\"]*?)['\"][^>]*?>", reviews)
        reviews = reviews.replace(m.group(0), "")

    # with open("reviews.raw", "a") as f:
    #     f.write(reviews)

    # Python 2 compatibility
    # reviews = reviews.encode('utf-8')

    xmldoc = minidom.parseString("<reviews>" + reviews + "</reviews>")

    reviews = [div for div in xmldoc.getElementsByTagName("div")
               if div.getAttribute('class') == "single-review"]

    for review in reviews:
        review_date = [span for span in review.getElementsByTagName('span')
                       if span.getAttribute('class') == "review-date"]

        if review_date:
            review_date = review_date[0].firstChild.nodeValue

        review_rating = [div for div in review.getElementsByTagName('div')
                         if div.getAttribute('class') == "review-info-star-rating"]

        if review_rating:
            review_rating = review_rating[0].childNodes[1].getAttribute('aria-label')

        div_review_body = [div for div in review.getElementsByTagName('div')
                           if div.getAttribute('class') == "review-body"]

        if div_review_body:
            review_title = [span for span in div_review_body[0].getElementsByTagName('span')
                            if span.getAttribute('class') == "review-title"]

            if review_title and review_title[0].firstChild:
                review_title = review_title[0].firstChild.nodeValue
            else:
                review_title = ""

            review_body = div_review_body[0].childNodes[2].nodeValue

        result.append({
            'title': review_title,
            'rating': review_rating,
            'body': review_body,
            # converting time.struct_time into datetime
            'date': datetime.datetime(*time.strptime(review_date, "%B %d, %Y")[:6])
        })

    return result


def save_reviews(application_id, reviews):

    reviews_to_insert = [(application_id, r['title'], r['rating'], r['body'], r['date']) for r in reviews]

    # with sqlite3.connect('reviews.db') as db:
    #     db.executemany('INSERT INTO reviews (app, title, body, date) '
    #                    'VALUES (?, ?, ?, ?)', reviews_to_insert)

    with psycopg2.connect(PostgreSQL.connection_string) as db:
        try:
            cursor = db.cursor()
            cursor.executemany('INSERT INTO reviews (app_id, title, rating, body, date) '
                               'VALUES (%s, %s, %s, %s, %s)', reviews_to_insert)

            db.commit()

        except Exception as ex:
            db.rollback()
            raise ex


if __name__ == '__main__':
    main()
