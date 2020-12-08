#!/usr/bin/env python3
from classes import LightPi as lp
from classes import SQLSprinkler as sprinkler
from classes import TV as tv
from firebase_admin import credentials, initialize_app, db
from time import sleep
cred = credentials.Certificate("resources/serviceAccountKey.json")
initialize_app(cred, {'databaseURL': 'https://new-project-3cddb-default-rtdb.firebaseio.com'})
time_to_sleep = 3
def main():
    tv.connect()
    while 1:
        ref = db.reference()
        lp.do_loop(ref)
        sprinkler.do_loop(ref)
        tv.do_loop(ref)
        sleep(time_to_sleep)
if __name__ == "__main__":
    main()
