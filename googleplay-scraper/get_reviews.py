__author__ = 'kevin'

import urllib.request
import urllib.parse
import json
import re
from xml.dom import minidom
import time
import sqlite3
import argparse
import datetime


def main():
    args = parse_args()

    max_pages = args.pages

    for page_number in range(1, max_pages):

        print("Sleeping...")
        time.sleep(5)

        response = make_request(args.application, page_number)
        print("Request made")

        reviews = parse_response(response)
        print("Response parsed")

        save_reviews(args.application, reviews)
        print("Reviews saved into the database")


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

    parser.add_argument("-app", "--application",
                        help="The id of the app to get the reviews from.")

    parser.add_argument("-p", "--pages", type=int,
                        help="The number of review pages to request.")

    return parser.parse_args()


def make_request(application_id, page_number):
    request = urllib.request.Request("https://play.google.com/store/getreviews", method="POST")

    request.add_header("content-type", "application/x-www-form-urlencoded; charset=utf-8")
    request.add_header("origin", "https://play.google.com")
    request.add_header("cache-control", "no-cache")
    # request.add_header("referer", "https://play.google.com/store/apps/details?id=com.github.mobile&hl=en")

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
    data = data.encode('utf-8')

    response = urllib.request.urlopen(request, data)

    return response


def parse_response(response):
    result = []

    # this is to turn the bytes that come in the response into a python string
    response = str(response.read(), "utf-8")

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

    xmldoc = minidom.parseString("<reviews>" + reviews + "</reviews>")

    reviews = [div for div in xmldoc.getElementsByTagName("div")
               if div.getAttribute('class') == "single-review"]

    for review in reviews:
        review_date = [span for span in review.getElementsByTagName('span')
                       if span.getAttribute('class') == "review-date"]

        if review_date:
            review_date = review_date[0].firstChild.nodeValue

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
            'body': review_body,
            # converting time.struct_time into datetime
            'date': datetime.datetime(*time.strptime(review_date, "%B %d, %Y")[:6])
        })

    return result


def save_reviews(application_id, reviews):

    reviews_to_insert = [(application_id, r['title'], r['body'], r['date']) for r in reviews]

    with sqlite3.connect('reviews.db') as db:
        db.executemany('INSERT INTO reviews (app, title, body, date) '
                       'VALUES (?, ?, ?, ?)', reviews_to_insert)


if __name__ == '__main__':
    main()
