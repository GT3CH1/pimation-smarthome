from pywebostv.discovery import *  # Because I'm lazy, don't do this.
from pywebostv.connection import *
from pywebostv.controls import *
import json
from os import getcwd

# 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
# 2. Go through the registration process. `store` gets populated in the process.
# 3. Persist the `store` state to disk.
# 4. For later runs, read your storage and restore the value of `store`.
store = {}
ip = ''
with open(getcwd() + '/resources/tv.json') as file:
    client = json.load(file)
    store = client['secret']
    ip = client['tv']['ip']
print("Key : " + str(store))
print("IP : " + ip)
# Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
# you could skip the slow scan and # instead simply say:
#    client = WebOSClient("<IP Address of TV>")
client = WebOSClient(str(ip))
def connect():
    client.connect()
    for status in client.register(store):
       if status == WebOSClient.PROMPTED:
           print("Please accept the connect on the TV!")
       elif status == WebOSClient.REGISTERED:
           print("Registration successful!")

# Keep the 'store' object because it contains now the access token
# and use it next time you want to register on the TV.
print(store)  # {'client_key': 'ACCESS_TOKEN_FROM_TV'}
