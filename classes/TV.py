from pywebostv.connection import *
from pywebostv.controls import *
from wakeonlan import send_magic_packet
import json
from os import system, environ
import pathlib

# Load the client key from environment.
store = {'client_key': environ.get("CLIENT_KEY")}

ip = None
mac = None
first_run = True
last_mute = True
last_power = False
last_vol = -1

media_client = None
system_client = None


def update_tv_state(ref, power_data, volume_data):
    """
    Updates the TV state in firebase.
    :param ref: The firebase reference.
    :param power_data: The JSON data containing the power state and remote state.
    :param volume_data: The JSON data containg the volume, mute, and remote state.
    :return:
    """
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
    """
    Checks the current tv power, firebase power, and firebase remote.
    If firebase power is on, and the remote flag is true, turn on the TV via WOL.
    If firebase power is off, and the remote flag is true, do nothing. This is handled in the loop.
    If the TV is on, and firebase power is off and remote is false, update firebase.
    If the TV is off, and firebase power is on and remote is false, update firebase.
    :param ref: The firebase reference.
    :return:
    """
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
            update_tv_state(ref, power_data, volume_data)
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
    elif not remote_on and command != 0:
        power_data['on'] = False
        print("TV is supposed to be off..")
        update_tv_state(ref, power_data, volume_data)
        return False


def wake_tv():
    """
    Wakes up the TV via WOL.
    :return: none.
    """
    global mac
    global ip
    print("Sending WOL packet to {0} ({1})".format(mac, ip))
    send_magic_packet(mac, ip_address=ip)


def connect():
    """
    Connects the media and system client to the TV.
    :return: none.
    """
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
def get_tv_volume():
    """
    Gets the current TV volume.
    :return: The current TV volume (mute state, volume). -1 if there was an error
    """
    global media_client
    try:
        current_tv_vol = media_client.get_volume()['volume']
        current_mute_state = media_client.get_volume()['muted']
    except Exception:
        current_tv_vol = -1
        current_mute_state = -1
        print("Could not get volume")
    return current_mute_state, current_tv_vol


def do_loop(ref):
    """
    Updates the volume and power of the tv.
    :param ref: The firebase reference.
    :return: none.
    """
    global media_client, system_client, mac
    data = ref.get()['upstairs-tv']
    firebase_volume = data['Volume']['currentVolume']
    firebase_volume_remote = data['Volume']['remote']
    firebase_mute = data['Volume']['isMuted']
    firebase_power = data['OnOff']['on']
    firebase_power_remote = data['OnOff']['remote']
    current_mute_state, current_tv_vol = get_tv_volume()

    volume_data = {
        'currentVolume': firebase_volume,
        'isMuted': firebase_mute,
        'remote': firebase_volume_remote
    }

    power_data = {
        'on': True,
        'remote': firebase_power_remote
    }
    if current_tv_vol > -1:
        if firebase_volume_remote:
            try:
                media_client.set_volume(firebase_volume)
                media_client.mute(firebase_mute)
                volume_data['remote'] = False
                print("Updating volume")
            except Exception:
                pass
        if not firebase_volume_remote:
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

    update_tv_state(ref, power_data, volume_data)
