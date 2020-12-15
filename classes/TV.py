from pywebostv.discovery import *  # Because I'm lazy, don't do this.
from pywebostv.connection import *
from pywebostv.controls import *
from wakeonlan import send_magic_packet
import json
from time import sleep
from os import system
from os import getcwd
from os import environ
import pathlib
# 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
# 2. Go through the registration process. `store` gets populated in the process.
# 3. Persist the `store` state to disk.
# 4. For later runs, read your storage and restore the value of `store`.
store = {'client_key' : environ.get("CLIENT_KEY")}
ip = None
mac = None
first_run = True 
last_mute = True
last_power = False
last_vol = -1

media_client = None
system_client = None
# Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
# you could skip the slow scan and # instead simply say:
#    client = WebOSClient("<IP Address of TV>")

def update_values(ref, power, volume, muted):
    stepsize = 1
#    print(" power: {0}, volume: {1}, muted: {2} ".format(power,volume,muted))
    data = {'upstairs-tv': { 'OnOff':{'on': power}, 'Volume': {'currentVolume': volume, 'stepSize': stepsize, 'isMuted': muted}}}
    ref.update(data)

def checkTvOnOff(ref):
    global last_power
    global mac
    global ip
    data = ref.get()['upstairs-tv']
    if (ip == None and mac == None):
        with open(str(pathlib.Path(__file__).parent.parent.absolute()) + '/resources/tv.json') as file: 
            clientdata = json.load(file)
            ip = clientdata['tv']['ip']
            mac = clientdata['tv']['mac']

    volume = data['Volume']['currentVolume']
    muted = data['Volume']['isMuted']
    firebase_onoff = data['OnOff']['on']
#    print("Last power status: {0}, firebase value: {1}".format(last_power,firebase_onoff))
    # pings the tv to see if it is on or off
    if(system('/usr/bin/ping '+ip+' -c 1 -w 1 > /dev/null ') == 0):
        if not last_power:
#            print("TV on, last power was false.")
            update_values(ref, True, volume, muted)
            last_power = True
        return True

        # If the TV is off and the status in firebase is on, turn it on.
    elif(firebase_onoff and not last_power):
        last_power = True
        print("Sending WOL packet to {0} ({1})".format(mac,ip))
        send_magic_packet(mac, ip_address=ip)
        return True
        #else:
        #   print("tv is suppoed to be off.")
        #   The tv is suppoed to be off.
        #   last_power = False
        #   if not last_power:
        #       update_values(ref, False, volume, muted)
    elif(firebase_onoff and last_power):
        last_power = False
        update_values(ref, False, volume, muted)
   
def connect():
    global first_run
    global media_client
    global system_client
    global store
    global ip
    global mac
    global last_power
    if first_run and last_power:
        client = WebOSClient(ip)
        try:
            client.connect()
        except Exception:
            pass
        register = client.register(store)
        for status in register:
                if status == 2:
                    first_run = True
        media_client = MediaControl(client)
        system_client = SystemControl(client)

def update_settings(ref):
    global last_vol
    global media_client
    try:
        current_tv_vol = media_client.get_volume()['volume']
        current_mute_state = media_client.get_volume()['muted']
    except Exception:
        current_tv_vol = ref.get()['upstairs-tv']['Volume']['currentVolume']
        current_mute_state = ref.get()['upstairs-tv']['Volume']['isMuted']
    firebase_vol = ref.get()['upstairs-tv']['Volume']
    if (current_tv_vol != firebase_vol['currentVolume']) or (firebase_vol['isMuted'] != current_mute_state):
#        print("Updating firebase.")
        update_values(ref,last_power,current_tv_vol,current_mute_state)
        return

def do_loop(ref):
    global first_run
    global last_vol
    global last_mute
    global last_power
    global media_client
    global system_client
    global mac
    data = ref.get()['upstairs-tv']
    vol = data['Volume']['currentVolume']
    isMuted = data['Volume']['isMuted']
    power = data['OnOff']['on']
    if (vol != last_vol) or (isMuted != last_mute):
        try:
            media_client.set_volume(vol) 
            media_client.mute(isMuted)
        except Exception:
            pass
        last_vol = vol
        last_mute = isMuted

    # Check the power status
    if power != last_power:
        last_power = power
        if not power:
            try:
                last_power = False
                print("Powering off TV.")
                system_client.power_off()
            except Exception:
                return
            return
    update_settings(ref)

# Keep the 'store' object because it contains now the access token
# and use it next time you want to register on the TV.
