__author__ = 'kevin'

import sqlite3


def main():

    db = sqlite3.connect('reviews.db')

    db.execute('''CREATE TABLE reviews (
                "id" INTEGER PRIMARY KEY,
                "app" TEXT NOT NULL,
                "title" TEXT NOT NULL,
                "body" TEXT NOT NULL
                );''')

    db.commit()
    db.close()

if __name__ == '__main__':
    main()
