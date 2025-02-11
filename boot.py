from asyncio import Event
import json

booted = Event()            # 0 - hier kann unterschieden werden ob das System schon an war oder neu gebootet ist
connectToWlan = Event()     # 1 - Wird gesetzt wenn gerade versucht wird eine Internetverbindung aufzubauen
checkForUpdates = Event()   # 2 - Es wird gerade nach Updates gesucht
deliverWebServer = Event()  # 3 - Der Webserver zum eingeben von SSID und Password fürs Wlan ist gerade aktiv
updateFirmware = Event()    # 4 - Die Firmware wird gerade aktualisiert
waitToCheck = Event()       # 5 - Es wird gerade gewartet um später nach Updates zu suchen


SSID = 'AlphaCentauri'
SSID_KEY = 'vhuj7240'


def connect_to_wlan(wlan):
    wlan.active(True)
    wlan.config(hostname='WordClock') # read from config
    if not wlan.isconnected():
        print('Connecting to network ', SSID, '...') # read ssid from config
        try:
            wlan.connect(SSID, SSID_KEY) # read ssid and key from config
        except OSError:
            wlan.active(False)
            wlan.active(True)
            wlan.connect(SSID, SSID_KEY) # read ssid and key from config


def get_config():
    f = open('config.json', 'r')
    return json.loads(f.read())


def change_config(key, value):
    config = get_config()
    config[key] = value
    f = open('config.json', 'r')
    f.write(json.dumps(config))
    f.close()


class BootStateMachine:
    def __init__(self):
        pass
    
    async def boot_device(self):
        # state 0
        pass

    async def connect_to_wlan(self):
        # state 1
        pass

    async def check_for_updates(self):
        # state 2
        pass

    async def deliver_webserver(self):
        # state 3
        pass

    async def update_firmware(self):
        # state 4
        pass

    async def wait_to_check_updates(self):
        # state 5
        pass


def main():
    print("Start System")
    change_config("test", "123")
    config = get_config()
    print(config['test'])


if __name__ == '__main__':
    main()