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
last_power = True
last_vol = -1

media_client = None
system_client = None
# Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
# you could skip the slow scan and # instead simply say:
#    client = WebOSClient("<IP Address of TV>")

def update_values(ref, power, volume, muted):
    stepsize = ref.get()['upstairs-tv']['Volume']['stepSize']
    print(" power: {0}, volume: {1}, muted: {2} ".format(power,volume,muted))
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

    # pings the tv to see if it is on or off
    if(system('/usr/bin/ping '+ip+' -c 1 -w 1 > /dev/null ') == 0):
        last_power = True
    volume = ref.get()['upstairs-tv']['Volume']['currentVolume']
    muted = ref.get()['upstairs-tv']['Volume']['isMuted']
        # If the TV is off and the status in firebase is on, turn it on.
    if(data['OnOff']['on']):
        last_power = True
        send_magic_packet(mac, ip_address=ip)
        update_values(ref, False, volume, muted)
        #else:
        #   print("tv is suppoed to be off.")
        #   The tv is suppoed to be off.
        #   last_power = False
        #   if not last_power:
        #       update_values(ref, False, volume, muted)
       
def connect():
    global first_run
    global media_client
    global system_client
    global store
    global ip
    global mac
    if first_run:
        client = WebOSClient(ip)
        client.connect()
        register = client.register(store)
        for status in register:
                if status == 2:
                    first_run = True
        media_client = MediaControl(client)
        system_client = SystemControl(client)

def update_settings(ref):
    global last_vol
    global media_client
    current_tv_vol = media_client.get_volume()
    current_mute_state = current_tv_vol['muted']
    firebase_vol = ref.get()['upstairs-tv']['Volume']
    if (current_tv_vol['volume'] != firebase_vol['currentVolume']) or (firebase_vol['isMuted'] != current_mute_state):
        print("Updating firebase.")
        update_values(ref,True,current_tv_vol['volume'],current_mute_state)
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
        first_run = False
        last_vol = vol
        last_mute = isMuted
        media_client.set_volume(vol) 
        media_client.mute(isMuted)
    # Check the power status
    if power != last_power:
        last_power = power
        # If firebase power is off, turn it off.
        if not power and last_power:
            try:
                system_client.power_off()
            except Exception:
                return
            return
    update_settings(ref)

# Keep the 'store' object because it contains now the access token
# and use it next time you want to register on the TV.
