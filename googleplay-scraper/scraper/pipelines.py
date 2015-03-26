import psycopg2

from scrapy import log
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher

from googleplay.config import *
from googleplay.googleplay import GooglePlayAPI

# Stores the APK information in the database
class SQLiteStorePipeline(object):
    filename = 'EvolutionOfAndroidApplications.sqlite'
    connection_string = "host='localhost' dbname='kac2375' user='kac2375' password='thisismypassword'"
    
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
            self.conn = psycopg2.connect(self.connection_string)
        except Exception as ex:
            log.msg('CONENCTION FAILED WOOT', level=log.DEBUG)
            log.msg('File does not exist: %s' % self.filename, level=log.ERROR)
 
    def finalize(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def insert_item(self, item):
        try:
            log.msg('EXECUTING QUERY WOOT', level=log.DEBUG)
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

            log.msg('QUERY EXECUTED WOOT', level=log.DEBUG)

        except Exception as ex:
            log.msg('ROLLING BACK QUERY WOOT', level=log.DEBUG)
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
