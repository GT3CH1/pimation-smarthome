import requests

SQL_URL = "http://pimation.peasenet.com/modules/SQLSprinkler/lib/api.php"
last_google_home_val = -1
last_google_home_bool = False
first_run = True
googleHomeBooleans = [None, False, False, False, False, False, False, False, False, False, False]
sqlSprinklerBooleans = [None, False, False, False, False, False, False, False, False, False, False]
sqlSprinklerJson = []

def do_loop(ref):
        global SQL_URL
        global last_google_home_val 
        global last_google_home_bool
        global googleHomeBooleans
        global sqlSprinklerBooleans
        global sqlSprinklerJson
        global first_run
        update_sql_sprinkler()
        data = ref.get()
        for sys_number in range(1, 11):
            sys_name = 'sprinkler-zone-' + str(sys_number)
            sys_data = data[sys_name]
            googleHomeBooleans[sys_number] = sys_data['OnOff']['on']
            if(googleHomeBooleans[sys_number] and first_run):
                last_google_home_val = sys_number
                first_run = False
                last_google_home_bool = True
        for i in range(1, len(googleHomeBooleans)):
            if not googleHomeBooleans[i]:
                if last_google_home_val == i and not googleHomeBooleans[i] and last_google_home_bool:
                    pin = str(sqlSprinklerJson[i - 1]['gpio'])
                    update_string = '?off=' + pin + '&sysval=' + str(i)
                    requests.get(url=SQL_URL + update_string)
                    last_google_home_bool = False
                    last_google_home_val = i
                    if not last_google_home_bool and last_google_home_val == i:
                        continue
                    for j in range(1, 11):
                        if googleHomeBooleans[i]:
                            sys_name = 'sprinkler-zone-' + str(j)
                            update_val = {sys_name: {'OnOff': {'on': False}}}
                            ref.update(update_val)
                            googleHomeBooleans[i] = False
                else:
                    continue
            else:
                if googleHomeBooleans[i] and sqlSprinklerBooleans[i]:
                    continue
                else:
                    pin = str(sqlSprinklerJson[i - 1]['gpio'])
                    update_string = '?on=' + pin + '&sysval=' + str(i)
                    requests.get(url=SQL_URL + update_string)
                    sys_name = 'sprinkler-zone-' + str(i)
                    update_val = {sys_name: {'OnOff': {'on': True}}}
                    ref.update(update_val)
                    last_google_home_val = i
                    last_google_home_bool = True
                for j in range(1, 11):
                    if googleHomeBooleans[j] and j != i:
                        sys_name = 'sprinkler-zone-' + str(j)
                        update_val = {sys_name: {'OnOff': {'on': False}}}
                        ref.update(update_val)
                        googleHomeBooleans[i] = False

def update_sql_sprinkler():
        global sqlSprinklerJson
        request = requests.get(url=SQL_URL + '?systems')
        json = request.json()
        sqlSprinklerJson = json
        boolean_loc = 1
        for system in sqlSprinklerJson:
            if system['status'] == 'off':
                sqlSprinklerBooleans[boolean_loc] = False
            else:
                sqlSprinklerBooleans[boolean_loc] = True
            boolean_loc = boolean_loc + 1
