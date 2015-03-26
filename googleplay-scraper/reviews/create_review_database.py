__author__ = 'kevin'

import sqlite3


'''
In PostgreSQL:

CREATE TABLE "reviews" (
  "id" SERIAL PRIMARY KEY,
  "app_id" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "body" TEXT NOT NULL,
  "date" TIMESTAMP NOT NULL
);
'''


def main():

    db = sqlite3.connect('reviews.db')

    db.execute('''CREATE TABLE reviews (
                "id" INTEGER PRIMARY KEY,
                "app" TEXT NOT NULL,
                "title" TEXT NOT NULL,
                "body" TEXT NOT NULL,
                "date" DATE NOT NULL
                );''')

    db.commit()
    db.close()

if __name__ == '__main__':
    main()
