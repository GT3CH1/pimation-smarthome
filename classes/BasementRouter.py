import requests
from os import environ

TOKEN = environ.get("JENKINS_KEY")
TOKEN_SAT = False
JENKINS_URL = ""
PREV_ON = False
def do_loop(ref):
    global JENKINS_URL
    if not TOKEN_SAT and len(TOKEN) > 0:
        JENKINS_URL = "https://ci.peasenet.com/generic-webhook-trigger/invoke?token="+TOKEN
    else:
        return
    do_reboot = ref.get()['rtr1']['RebootNow']['reboot']
    if do_reboot:
        data = {'rtr1': { 'RebootNow': {'reboot': False } } }
        ref.update(data)
        result = requests.get(url=JENKINS_URL)
        json = result.json()
        print("Basement router reboot: {0} ".format(json['jobs']['rtr1 reboot']['triggered'])) 
