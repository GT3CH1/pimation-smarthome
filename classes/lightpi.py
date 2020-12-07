class lightpi:
    def do_loop(self):
        global PREV_ON
        on = ref.get()['1']['OnOff']['on']
        if(on != PREV_ON):
            if(on == True):
                PARAMS = {'status':'on'}
                print(sending on)
            else:
                PARAMS = {'status':'off'}
                print(sending off)
            requests.get(url = LIGHT_URL+submit.php, params = PARAMS)
            PREV_ON = on
    def __init__(self):
        self.do_loop()
