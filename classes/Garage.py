import requests

GARAGE_URL = "https://pimation.peasenet.com/modules/garage/"
PREV_OPEN = 0
FIRST_RUN = True
garage_data = {
    'garage-door':
        {
            'OpenClose': {
                'openPercent': 0,
                'remote': False
            }
        }
}


def do_loop(ref):
    global GARAGE_URL
    global PREV_OPEN
    global FIRST_RUN
    if FIRST_RUN:
        ref.update(garage_data)
        FIRST_RUN = False
    is_remote = ref['garage-door']['OpenClose']['remote']
    if is_remote:
        print("Toggling garage...")
        params = {'toggle': '1'}
        requests.post(url=GARAGE_URL + "submit.php", data=params)
        garage_data['garage-door']['OpenClose']['remote'] = False
        ref.update(garage_data)