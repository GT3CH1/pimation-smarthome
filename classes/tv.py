class tvOnOff:
    def do_loop(self):
        global prev_tv_vol
        global prev_tv_onoff
        vol = ref.get()['upstairs-tv']['Volume']['currentVolume']
        onoff = ref.get()['upstairs-tv']['OnOff']['on']
        if vol != prev_tv_vol:
            print('running vol')
            prev_tv_vol = vol
            subprocess.call('/root/lgtv2/script.sh vol ' + str(vol),shell=True)
            print('done with tv.')
        # TODO: fix power issue on tv

    def __init__(self):
        self.do_loop()
