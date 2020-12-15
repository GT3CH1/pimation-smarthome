import requests
GARAGE_URL = "https://pimation.peasenet.com/modules/garage/"
PREV_OPEN = 0
def do_loop(ref):
         global GARAGE_URL
         global PREV_OPEN
         curropen = ref.get()['garage-door']['OpenClose']['openPercent']
         if curropen != PREV_OPEN:
            print("Toggling garage...")
            params = {'toggle': '1'} 
            requests.post(url=GARAGE_URL + "submit.php", data=params)
            PREV_OPEN = curropen
            print("PREV_OPEN sat properly: {0}".format(PREV_OPEN == curropen)) 
