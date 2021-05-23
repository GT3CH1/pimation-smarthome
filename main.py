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


def main(argv):
    lgtv_first_run = True
    time_to_sleep = 1
    module_name = ''
    try:
        opts, args = getopt.getopt(argv, "m:t:")
    except getopt.GetoptError:
        print("Usage: ./main.py -m module -t refresh_time")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-m':
            module_name = arg
        elif opt == '-t':
            time_to_sleep = int(arg)
    print("Module: {0}, sleep: {1}".format(module_name, time_to_sleep))
    if not len(module_name) >= 2:
        print("Error: Need a module name to run.")
        sys.exit(2)
    while 1:
        ref = db.reference()
        if module_name == "garage" or module_name == "all":
            garage.do_loop(ref)
        if module_name == "br" or module_name == "all":
            br.do_loop(ref)
        if module_name == "lightpi" or module_name == "all":
            lp.do_loop(ref)
        if module_name == "sprinkler" or module_name == "all":
            sprinkler.do_loop(ref)
        if module_name == "tv" or module_name == "all":
            power_on = lgtv.check_tv_power(ref)
            if power_on:
                lgtv.connect()
                lgtv.do_loop(ref)
        sleep(time_to_sleep)


if __name__ == "__main__":
    main(sys.argv[1:])
