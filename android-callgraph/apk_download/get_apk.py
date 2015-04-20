__author__ = 'kevin'

import argparse
import os

from googleplay.config import *
from googleplay.googleplay import GooglePlayAPI


def main():
    args = parse_args()
    get_apk(args.application, args.output_path)


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

    parser.add_argument("-a", "--application",
                        help="The id of the app to get the apk from.")

    parser.add_argument("-o", "--output_path",
                        help="the folder where to save the downloaded apk.")

    return parser.parse_args()


def get_apk(package_name, output_path):
    download_filename = os.path.join(output_path, package_name + ".apk")

    # Connect
    api = GooglePlayAPI(ANDROID_ID)
    api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)

    # Get the version code and the offer type from the app details
    m = api.details(package_name)
    doc = m.docV2
    vc = doc.details.appDetails.versionCode
    ot = doc.offer[0].offerType

    # Download
    print("Downloading APK...")

    data = api.download(package_name, vc, ot)
    open(download_filename, 'wb').write(data)


if __name__ == '__main__':
    main()
