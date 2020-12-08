from pywebostv.discovery import *  # Because I'm lazy, don't do this.
from pywebostv.connection import *
from pywebostv.controls import *
from wakeonlan import send_magic_packet
import json
from os import getcwd
from os import environ

# 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
# 2. Go through the registration process. `store` gets populated in the process.
# 3. Persist the `store` state to disk.
# 4. For later runs, read your storage and restore the value of `store`.
store = {'client_key' : environ.get("CLIENT_KEY")}
ip = None
mac = None
first_run = True 
last_power = True
last_vol = -1

media_client = None
system_client = None
# Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
# you could skip the slow scan and # instead simply say:
#    client = WebOSClient("<IP Address of TV>")

def connect():
    global first_run
    global media_client
    global system_client
    global store
    global ip
    global mac
    ip = None
    with open(getcwd() + '/resources/tv.json') as file:
        clientdata = json.load(file)
        ip = clientdata['tv']['ip']
        mac = clientdata['tv']['mac']
    if first_run:
        client = WebOSClient(ip)
        client.connect()
        print("Key : " + str(store))
        register = client.register(store)
        for status in register:
                print(status)
                if status == 2:
                    first_run = True
        media_client = MediaControl(client)
        system_client = SystemControl(client)
        print("Setting up media client.")

def update_settings(ref):
    global last_vol
    global media_client
    current_tv_vol = media_client.get_volume()
    firebase_vol = ref.get()['upstairs-tv']['Volume']['currentVolume']
    if(current_tv_vol != firebase_vol):
        data = {'upstairs-tv': { 'Volume': {'currentVolume': current_tv_vol}}}
        ref.update(data)
        print("updating tv volume")

def do_loop(ref):
    global first_run
    global last_vol
    global last_power
    global media_client
    global system_client
    global mac
    data = ref.get()['upstairs-tv']
    vol = data['Volume']['currentVolume']
    #power = data['OnOff']['on']
    if vol != last_vol:
        print("Changing vol.")
        first_run = False
        last_vol = vol
        media_client.set_volume(vol) 
    #if power != last_power:
    #    print("Changing power.")
    #    last_power = power
    #    if not power:
    #        system_client.power_off()
    update_settings(ref)

# Keep the 'store' object because it contains now the access token
# and use it next time you want to register on the TV.
print(store)  # {'client_key': 'ACCESS_TOKEN_FROM_TV'}
