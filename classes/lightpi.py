import requests
LIGHT_URL = "http://lightpi.peasenet.com/"
PREV_ON = False


class LightPi:
    def do_loop(self, ref):
        global PREV_ON
        on = ref.get()['1']['OnOff']['on']
        if on != PREV_ON:
            if on:
                params = {'status': 'on'}
                print("sending on")
            else:
                params = {'status': 'off'}
                print("sending off")
            requests.get(url=LIGHT_URL + "submit.php", params=params)
            PREV_ON = on

    def __init__(self):
        self.do_loop()
