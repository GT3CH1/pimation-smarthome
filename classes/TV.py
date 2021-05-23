from pywebostv.connection import *
from pywebostv.controls import *
from wakeonlan import send_magic_packet
import json
from os import system, environ
import pathlib

# 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
# 2. Go through the registration process. `store` gets populated in the process.
# 3. Persist the `store` state to disk.
# 4. For later runs, read your storage and restore the value of `store`.

store = {'client_key': environ.get("CLIENT_KEY")}
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

def update_values(ref, power_data, volume_data):
    # media_state = ref.get()['MediaState']
    # current_application = ref.get()['currentApplication']['currentApplication']
    # current_input = ref.get()['currentInput']['currentInput']
    data = {
        'upstairs-tv': {
            'OnOff': power_data,
            'Volume': volume_data
            # 'MediaState': media_state,
            # 'currentInput': {'currentInput': current_input},
            # 'currentApplication': {'currentApplication': current_application}
        }
    }
    print(data)
    ref.update(data)


def check_tv_power(ref):
    global last_power
    global mac
    global ip
    data = ref.get()['upstairs-tv']

    if ip is None and mac is None:
        path = str(pathlib.Path(__file__).parent.parent.absolute()) + '/resources/tv.json'
        print("Loading {0}".format(path))
        with open(path) as file:
            client_data = json.load(file)
            ip = client_data['tv']['ip']
            mac = client_data['tv']['mac']

    volume = data['Volume']['currentVolume']
    muted = data['Volume']['isMuted']
    vol_remote = data['Volume']['remote']
    firebase_on_off = data['OnOff']['on']
    remote_on = data['OnOff']['remote']

    volume_data = {
        'currentVolume': volume,
        'isMuted': muted,
        'remote': vol_remote
    }

    power_data = {
        'on': True,
        'remote': remote_on
    }

    # This returns 0 when the tv is pingable.
    command = system('/usr/bin/ping ' + ip + ' -c 1 -w 1 > /dev/null ')
    if command == 0:
        if not remote_on:
            update_values(ref, power_data, volume_data)
            print("Setting firebase power to on")
        return True

    # If the TV is off and the remote flag is enabled, turn on the tv.
    elif (firebase_on_off and remote_on) and command != 0:
        wake_tv()
        time.sleep(3000)
        return True
    elif not firebase_on_off and not remote_on:
        print("Both firebase remote and power are false")
        return False
    elif not firebase_on_off and remote_on:
        print("TV needs to turn off.")
        return True
    else:
        print("TV is supposed to be off..")
        return False


def wake_tv():
    global mac
    global ip
    print("Sending WOL packet to {0} ({1})".format(mac, ip))
    send_magic_packet(mac, ip_address=ip)


def connect():
    global media_client
    global system_client
    global store
    global ip
    global mac
    global last_power
    client = WebOSClient(ip)
    try:
        print("Connecting...")
        client.connect()
        register = client.register(store, timeout=3)
        for status in register:
            if status == 2:
                print("Connected!")
                media_client = MediaControl(client)
                system_client = SystemControl(client)
    except Exception:
        print("Could not connect.")
        pass


# Gets the current volume and mute state from our TV
def get_tv_volume(ref):
    global media_client
    try:
        current_tv_vol = media_client.get_volume()['volume']
        current_mute_state = media_client.get_volume()['muted']
    except Exception:
        current_tv_vol = ref.get()['upstairs-tv']['Volume']['currentVolume']
        current_mute_state = ref.get()['upstairs-tv']['Volume']['isMuted']
    return current_mute_state, current_tv_vol


# The main chunk of code.
def do_loop(ref):
    global media_client, system_client, mac
    data = ref.get()['upstairs-tv']
    firebase_volume = data['Volume']['currentVolume']
    firebase_mute = data['Volume']['isMuted']
    firebase_power = data['OnOff']['on']
    firebase_power_remote = data['OnOff']['remote']
    firebase_volume_remote = data['Volume']['remote']
    current_mute_state, current_tv_vol = get_tv_volume(ref)

    volume_data = {
        'currentVolume': current_tv_vol,
        'isMuted': firebase_mute,
        'remote': firebase_volume_remote
    }

    power_data = {
        'on': True,
        'remote': firebase_power_remote
    }

    if ((firebase_volume != current_tv_vol) or (firebase_mute != current_mute_state)) and firebase_volume_remote:
        try:
            media_client.set_volume(firebase_volume)
            media_client.mute(firebase_mute)
            current_tv_vol = firebase_volume
            current_mute_state = firebase_mute
            firebase_volume_remote = False
        except Exception:
            pass
    if ((firebase_volume != current_tv_vol) or (firebase_mute != current_mute_state)) and not firebase_volume_remote:
        volume_data['currentVolume'] = current_tv_vol
        volume_data['isMuted'] = current_mute_state
        volume_data['remote'] = False
    if not firebase_power and firebase_power_remote:
        try:
            power_data['remote'] = False
            power_data['on'] = False
            print("Powering off TV.")
            system_client.power_off()
        except Exception:
            pass

    update_values(ref, power_data, volume_data)
    return
