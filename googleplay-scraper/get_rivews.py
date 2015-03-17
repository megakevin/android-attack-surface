__author__ = 'kevin'

import urllib.request
import urllib.parse
import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv


def main():

    max_pages = 10

    csv_file = open("reviews.csv", "a", newline='')
    csv_writer = csv.writer(csv_file)

    raw_file = open("raw.html", "a", newline='')

    for page_number in range(1, max_pages):

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
                                       'pageNum': 1,
                                       'id': "com.github.mobile",
                                       'reviewSortOrder': "0",
                                       'xhr': "1",
                                       'token': "oCu4PNapSrAMxh2-vqD_iMxod_g:1394178244711"})
        data = data.encode('utf-8')

        response = urllib.request.urlopen(request, data)

        # this is to turn the bytes that come in the response into a python string
        response = str(response.read(), "utf-8")

        # apparently random garbage
        response = response.replace(")]}'", " ")

        # this converts the string to json and takes care of all unescaping
        response = json.loads(response)

        reviews = response[0][2]

        # deleting all <img> tags because since they don't close, they are not valid xml
        while re.search(r"<img\s[^>]*?src\s*=\s*['\"]([^'\"]*?)['\"][^>]*?>", reviews):
            m = re.search(r"<img\s[^>]*?src\s*=\s*['\"]([^'\"]*?)['\"][^>]*?>", reviews)
            reviews = reviews.replace(m.group(0), "")

        raw_file.write(reviews)

        xmldoc = minidom.parseString("<reviews>" + reviews + "</reviews>")

        divs = xmldoc.getElementsByTagName("div")
        for div in divs:
            if div.getAttribute('class') == "review-body":

                review_title = ""
                if div.childNodes[1].firstChild:
                    review_title = div.childNodes[1].firstChild.nodeValue

                review_body = div.childNodes[2].nodeValue

                # TODO: Write to database instead
                csv_writer.writerow([review_title, review_body])

                print(review_title + ">" + review_body)


if __name__ == '__main__':
    main()
