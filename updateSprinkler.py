#!/usr/bin/env python
from time import sleep
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials

import requests
cred = credentials.Certificate("resources/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://new-project-3cddb-default-rtdb.firebaseio.com'})
ref = db.reference()
URL = "http://pimation.peasenet.com/modules/SQLSprinkler/lib/api.php"
PREV_ON = False
time_to_sleep=5
while 1:
    data = ref.get()
    booleans = [None,False,False,False,False,False,False,False,False,False,False]
    for sysnumber in range(1,11):
        sysname = 'sprinkler-zone-'+str(sysnumber)
        sysdata = data[sysname]
        booleans[sysnumber] = sysdata['OnOff']['on']
        print(booleans[sysnumber])
    sleep(time_to_sleep)
