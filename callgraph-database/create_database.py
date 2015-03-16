__author__ = 'kevin'

import sqlite3


def main():

    db = sqlite3.connect('android.cg.db')

    db.execute('''CREATE TABLE edges (
                "id" INTEGER PRIMARY KEY,
                "caller" TEXT NOT NULL,
                "caller_package" TEXT NOT NULL,
                "caller_class" TEXT NOT NULL,
                "callee" TEXT NOT NULL,
                "callee_package" TEXT NOT NULL,
                "callee_class" TEXT NOT NULL,
                "app" TEXT NOT NULL
                );''')

    db.commit()
    db.close()

if __name__ == '__main__':
    main()
