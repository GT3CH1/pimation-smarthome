#!/usr/bin/env python3
from classes import LightPi as lp
from classes import SQLSprinkler as sprinkler
from classes import TV as tv
from firebase_admin import credentials, initialize_app, db
from time import sleep
import pathlib
import sys
cred = credentials.Certificate(str(pathlib.Path(__file__).parent.absolute()) + "/resources/serviceAccountKey.json")
initialize_app(cred, {'databaseURL': 'https://new-project-3cddb-default-rtdb.firebaseio.com'})
time_to_sleep = 3
tv_first_run = False
def main():
    arg = None
    global tv_first_run
    if len(sys.argv) != 2:
        print("Need two arguments!")
        return
    else:
        arg = sys.argv[1]
    while 1:
        ref = db.reference()
        if arg == "lightpi" or arg == "all":
            lp.do_loop(ref)
        if arg == "sprinkler" or arg == "all":
            sprinkler.do_loop(ref)

        if((arg == "tv" or arg == "all") and tv.checkTvOnOff(ref)):
            if not tv_first_run:
                tv.connect()
                tv_first_run = True
                tv.do_loop(ref)
            else:
                tv.do_loop(ref)
        sleep(time_to_sleep)
if __name__ == "__main__":
    main()
