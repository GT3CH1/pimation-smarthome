#!/usr/bin/env python3
from classes import LightPi as lp
from classes import SQLSprinkler as sprinkler
from classes import TV as lgtv
from classes import Garage as garage
from classes import BasementRouter as br
from firebase_admin import credentials, initialize_app, db

from time import sleep

import pathlib
import sys
import getopt

cred = credentials.Certificate(str(pathlib.Path(__file__).parent.absolute()) + "/resources/serviceAccountKey.json")
initialize_app(cred, {'databaseURL': 'https://new-project-3cddb-default-rtdb.firebaseio.com'})
time_to_sleep = 1
lgtv_first_run = True
def main():
    arg = None
    lgtv_first_run = True
    if len(sys.argv) != 2:
        print("Need two arguments!")
        return
    else:
        arg = sys.argv[1]
    while 1:
        ref = db.reference()
        if arg == "garage" or arg == "all":
            garage.do_loop(ref)
        if arg == "br" or arg == "all":
            br.do_loop(ref)
        if arg == "lightpi" or arg == "all":
            lp.do_loop(ref)
        if arg == "sprinkler" or arg == "all":
            sprinkler.do_loop(ref)
        if((arg == "tv" or arg == "all") and lgtv.checkTvOnOff(ref)):
            if lgtv_first_run:
                lgtv.connect()
                lgtv_first_run = False
                lgtv.do_loop(ref)
            else:
                lgtv.do_loop(ref)
        sleep(time_to_sleep)
if __name__ == "__main__":
    main()
