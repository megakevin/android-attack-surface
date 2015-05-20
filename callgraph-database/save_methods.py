__author__ = 'kevin'

import argparse
import psycopg2

from connection import PostgreSQL


def main():
    args = parse_args()
    load_database(args.methodlistfile)


def load_database(methodlistfile):

    methods_to_insert = list()

    with open(methodlistfile) as f:
        methods = f.read().splitlines()

    for method in methods:
        method_full_name = method
        method_package, method_class = get_decomposed_name(method)

        methods_to_insert.append((method_full_name, method_package, method_class))

    print("file loaded into memory")

    db = psycopg2.connect(PostgreSQL.connection_string)
    c = db.cursor()

    c.executemany('''INSERT INTO output_methods (
                     method, method_package, method_class)
                     VALUES (%s, %s, %s)''', methods_to_insert)

    db.commit()
    c.close()
    db.close()

    print("file loaded into database")


def get_decomposed_name(method):

    class_name = ".".join(method.split('.')[:-1])
    package_name = ".".join(class_name.split('.')[:-1])

    return package_name, class_name


def parse_args():
    """
        Provides a command line interface.

        Defines all the positional and optional arguments along with their respective valid values
        for the command line interface and returns all the received arguments as an object.

        Returns:
            An object that contains all the provided command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes a software's source code and reports various metrics related to it's attack surface.")

    parser.add_argument("-l", "--methodlistfile",
                        help="The file containing the method list to save's output")

    return parser.parse_args()


if __name__ == '__main__':
    main()
