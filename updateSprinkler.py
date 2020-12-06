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
time_to_sleep = 1


class google_home:
    googleHomeBooleans = [None, False, False, False, False, False, False, False, False, False, False]
    sqlSprinklerBooleans = [None, False, False, False, False, False, False, False, False, False, False]
    sqlSprinklerJson = []
    last_val = -1

    def do_loop(self):
        while 1:
            google_home.update_sql_sprinkler(self)
            data = ref.get()
            for sys_number in range(1, 11):
                sys_name = 'sprinkler-zone-' + str(sys_number)
                sys_data = data[sys_name]
                self.googleHomeBooleans[sys_number] = sys_data['OnOff']['on']
            for i in range(1,len(self.sqlSprinklerBooleans)):
                if(self.sqlSprinklerBooleans[i] == True):
                    sys_name = 'sprinkler-zone-' + str(i)
                    update_val = {sys_name: { 'OnOff': { 'on': True } } }
                    ref.update(update_val)
            if self.googleHomeBooleans != self.sqlSprinklerBooleans:
                for i in range(1, len(self.googleHomeBooleans)):
                    if self.googleHomeBooleans[i] != self.sqlSprinklerBooleans[i-1]:
                        if self.googleHomeBooleans[i] and (i != self.last_val):
                            pin = str(self.sqlSprinklerJson[i-1]['gpio'])
                            print("gpio pin: " + pin)
                            update_string = '?on='+pin
                            requests.get(url=URL+update_string)
                            sys_name = 'sprinkler-zone-' + str(i)
                            update_val = {sys_name: { 'OnOff': { 'on': True } } }
                            ref.update(update_val)
                            self.last_val = i
                        elif self.googleHomeBooleans[i] and not self.sqlSprinklerBooleans[i-1]:
                            continue
                        elif not self.googleHomeBooleans[i] and not self.sqlSprinklerBooleans[i-1]:
                            requests.get(url=URL+"?off")
            sleep(time_to_sleep)

    def update_sql_sprinkler(self):
        request = requests.get(url=URL + '?systems')
        json = request.json()
        self.sqlSprinklerJson = json
        boolean_loc = 1
        for system in self.sqlSprinklerJson:
            if system['status'] == 'off':
                self.sqlSprinklerBooleans[boolean_loc] = False
            else:
                self.sqlSprinklerBooleans[boolean_loc] = True
            boolean_loc = boolean_loc + 1

    def __init__(self):
        self.do_loop()


if __name__ == "__main__":
    google_home()
