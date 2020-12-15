import requests
LIGHT_URL = "https://lightpi.peasenet.com/"
PREV_ON = False
def do_loop(ref):
         global LIGHT_URL
         global PREV_ON
         on = ref.get()['1']['OnOff']['on']
         if on != PREV_ON:
            if on:
                params = {'status': 'on'}
            else:
                params = {'status': 'off'}
            print("Turning {0} rock garden lights".format("on" if on else "off"))
            requests.get(url=LIGHT_URL + "submit.php", params=params)
            PREV_ON =on
