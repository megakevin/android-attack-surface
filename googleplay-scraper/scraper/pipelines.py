import psycopg2

from scrapy import log
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher

from googleplay.config import *
from googleplay.googleplay import GooglePlayAPI

from connection import PostgreSQL

import urllib2
import urllib

import json
import re
from xml.dom import minidom
import time
# import sqlite3
import datetime


# Stores the APK information in the database
class SQLiteStorePipeline(object):
    filename = 'EvolutionOfAndroidApplications.sqlite'
    
    def __init__(self):
        self.conn = None
        dispatcher.connect(self.initialize, signals.engine_started)
        dispatcher.connect(self.finalize, signals.engine_stopped)

    def process_item(self, item, spider):
        # Tries to insert the APK file's information into the database.
        # If an error occurs or the APK file is a duplicate, the APK file 
        # is not downloaded and the APK file's information is not inserted 
        # into the database.
        try:
            self.insert_item(item)
            return item
        except Exception as e:
            raise DropItem('%s <%s>' % (e.message, item['url']))

    def initialize(self):
        # if path.exists(self.filename):
        #     self.conn = sqlite3.connect(self.filename)
        # else:
        #     log.msg('File does not exist: %s' % self.filename, level=log.ERROR)
        try:
            log.msg('CONNECTING WOOT', level=log.DEBUG)
            self.conn = psycopg2.connect(PostgreSQL.connection_string)
        except Exception as ex:
            log.msg('CONENCTION FAILED WOOT', level=log.DEBUG)
            log.msg(ex.message, level=log.DEBUG)
            log.msg('File does not exist: %s' % self.filename, level=log.ERROR)
 
    def finalize(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def insert_item(self, item):
        try:
            log.msg('INSERTING APK INFO WOOT', level=log.DEBUG)
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO ApkInformation ('
                           'Name, ApkName, Version, Developer, Genre, UserRating, NumberOfReviews, DatePublished, '
                           'FileSize, NumberOfDownloads, OperatingSystems, URL, SourceId, '
                           'ApkId, CollectionDate, LowerDownloads, UpperDownloads) '
                           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (item['name'], item['apk_name'], item['software_version'], item['developer'], item['genre'],
                            item['score'], item['num_reviews'], item['date_published'], item['file_size'], item['num_downloads'],
                            item['operating_systems'], item['url'], item['source_id'], item['id'],
                            item['collection_date'], item['lower_downloads'], item['upper_downloads']))

            self.conn.commit()
            cursor.close()

            log.msg('APK INFO INSERTED WOOT', level=log.DEBUG)

        except Exception as ex:
            log.msg('ROLLING BACK APK INFO INSERTION WOOT', level=log.DEBUG)
            log.msg(ex.message, level=log.ERROR)
            self.conn.rollback()

        # self.conn.execute('INSERT INTO ApkInformation (Name, Version, Developer, Genre, UserRating, DatePublished, FileSize, NumberOfDownloads, OperatingSystems, URL, SourceId, ApkId, CollectionDate, LowerDownloads, UpperDownloads) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (item['name'], item['software_version'], item['developer'], item['genre'], item['score'], item['date_published'], item['file_size'], item['num_downloads'], item['operating_systems'], item['url'], item['source_id'], item['id'], item['collection_date'], item['lower_downloads'], item['upper_downloads']))
        # 
        # log.msg('sdasda', level=log.ERROR)
        # log.msg(item['name'], level=log.ERROR)


# Uses https://github.com/egirault/googleplay-api to download APK files from Google Play
class GooglePlayDownloadPipeline(object):
    def process_item(self, item, spider):
        if item['source_id'] == 2:
            package_name = item['apk_name']  # item['url'][item['url'].find('id=') + 3:]
            filename = 'downloads/%s.apk' % item['apk_name']

            # Connect
            api = GooglePlayAPI(ANDROID_ID)
            api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)

            # Get the version code and the offer type from the app details
            m = api.details(package_name)
            doc = m.docV2
            vc = doc.details.appDetails.versionCode
            ot = doc.offer[0].offerType

            # Download
            log.msg('DOWNLOADING APK WOOT', level=log.DEBUG)
            log.msg('Downloading file from <%s>' % item['url'], level=log.INFO)
            data = api.download(package_name, vc, ot)
            try:
                log.msg('SAVING DOWNLOADED APK WOOT', level=log.DEBUG)
                open(filename, 'wb').write(data)
            except IOError as e:
                log.msg('EXCEPTION WHILE DOWNLOADING APK WOOT', level=log.DEBUG)
                log.msg('%s <%s>' % (e, item['url']), level=log.ERROR)
        return item


class ReviewsDownloadPipeline(object):
    def process_item(self, item, spider):
        if item['source_id'] == 2:
            package_name = item['apk_name']
            number_of_reviews = item['num_reviews']

            self.get_reviews(package_name, number_of_reviews)

        return item

    def get_reviews(self, application, number_of_reviews):
        page_size = 40

        # calculate the number of pages to request to obtain the given number of reviews
        max_pages = int(number_of_reviews / page_size) + 1

        for page_number in range(1, max_pages + 1):

            log.msg('SLEEPING BEFORE REQUESTING REVIEWS WOOT', level=log.DEBUG)
            time.sleep(5)

            response = self.make_request(application, page_number)
            log.msg('REVIEWS REQUESTED WOOT', level=log.DEBUG)

            reviews = self.parse_response(response)

            self.save_reviews(application, reviews)
            log.msg('REVIEWS SAVED WOOT', level=log.DEBUG)

    def make_request(self, application_id, page_number):
        request = urllib2.Request("https://play.google.com/store/getreviews")

        request.add_header("content-type", "application/x-www-form-urlencoded; charset=utf-8")
        request.add_header("origin", "https://play.google.com")
        request.add_header("cache-control", "no-cache")
        # request.add_header("referer", "https://play.google.com/store/apps/details?id=com.github.mobile&hl=en")

        request.add_header("referer", "https://play.google.com/store")
        request.add_header("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36")

        request.add_header("x-client-data", "CJW2yQEIpbbJAQiptskBCJ6SygEIrZXKARiricoB")
        request.add_header("x-requested-with", "XMLHttpRequest")

        data = urllib.urlencode({'reviewType': "0",
                                 'pageNum': page_number,
                                 'id': application_id,  # "com.github.mobile"
                                 'reviewSortOrder': "0",
                                 'xhr': "1",
                                 'token': "oCu4PNapSrAMxh2-vqD_iMxod_g:1394178244711"})
        data = data.encode('utf-8')

        response = urllib2.urlopen(request, data)

        return response

    def parse_response(self, response):
        result = []

        # this is to turn the bytes that come in the response into a python string
        response = str(response.read())

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

        reviews = reviews.encode('utf-8')

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

    def save_reviews(self, application_id, reviews):
        reviews_to_insert = [(application_id, r['title'], r['body'], r['date']) for r in reviews]

        with psycopg2.connect(PostgreSQL.connection_string) as db:
            try:
                cursor = db.cursor()
                cursor.executemany('INSERT INTO reviews (app_id, title, body, date) '
                                   'VALUES (%s, %s, %s, %s)', reviews_to_insert)
                db.commit()
            except Exception as ex:
                log.msg('REVIEWS INSERTION FAILED WOOT', level=log.DEBUG)
                log.msg(ex.message, level=log.DEBUG)
                db.rollback()
                raise ex