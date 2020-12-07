import requests

SQL_URL = "http://pimation.peasenet.com/modules/SQLSprinkler/lib/api.php"
last_google_home_val = -1
last_google_home_bool = False


class SQLSprinkler:
    googleHomeBooleans = [None, False, False, False, False, False, False, False, False, False, False]
    sqlSprinklerBooleans = [None, False, False, False, False, False, False, False, False, False, False]
    sqlSprinklerJson = []

    def do_loop(self, ref):
        global last_google_home_val
        global last_google_home_bool
        self.update_sql_sprinkler()
        data = ref.get()
        for sys_number in range(1, 11):
            sys_name = 'sprinkler-zone-' + str(sys_number)
            sys_data = data[sys_name]
            self.googleHomeBooleans[sys_number] = sys_data['OnOff']['on']
        for i in range(1, len(self.googleHomeBooleans)):
            if not self.googleHomeBooleans[i]:
                if last_google_home_val == i and not self.googleHomeBooleans[i]:
                    pin = str(self.sqlSprinklerJson[i - 1]['gpio'])
                    update_string = '?off=' + pin + '&sysval=' + str(i)
                    requests.get(url=SQL_URL + update_string)
                    last_google_home_bool = False
                    last_google_home_val = i
                    if last_google_home_val == i:
                        continue
                    print("Turning off: " + str(i))
                    for j in range(1, 11):
                        if self.googleHomeBooleans[i]:
                            sys_name = 'sprinkler-zone-' + str(j)
                            update_val = {sys_name: {'OnOff': {'on': False}}}
                            ref.update(update_val)
                            self.googleHomeBooleans[i] = False
                else:
                    continue
            else:
                if last_google_home_val == i and (self.googleHomeBooleans[i] and last_google_home_bool):
                    continue
                elif self.googleHomeBooleans[i] and not self.sqlSprinklerBooleans[i]:
                    if self.googleHomeBooleans[i] and self.sqlSprinklerBooleans[i]:
                        continue
                    else:
                        pin = str(self.sqlSprinklerJson[i - 1]['gpio'])
                        update_string = '?on=' + pin + '&sysval=' + str(i)
                        requests.get(url=SQL_URL + update_string)
                        sys_name = 'sprinkler-zone-' + str(i)
                        update_val = {sys_name: {'OnOff': {'on': True}}}
                        ref.update(update_val)
                        last_google_home_val = i
                        last_google_home_bool = True
                        print("Turning on:  " + str(i))
                        for j in range(1, 11):
                            if j == i:
                                continue
                            if self.googleHomeBooleans[i]:
                                sys_name = 'sprinkler-zone-' + str(j)
                                update_val = {sys_name: {'OnOff': {'on': False}}}
                                ref.update(update_val)
                                self.googleHomeBooleans[i] = False

    def update_sql_sprinkler(self):
        request = requests.get(url=SQL_URL + '?systems')
        json = request.json()
        self.sqlSprinklerJson = json
        boolean_loc = 1
        for system in self.sqlSprinklerJson:
            if system['status'] == 'off':
                self.sqlSprinklerBooleans[boolean_loc] = False
            else:
                self.sqlSprinklerBooleans[boolean_loc] = True
            boolean_loc = boolean_loc + 1

    def __init__(self, ref=None):
        self.do_loop(ref)
