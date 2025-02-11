import network
from asyncio import Event

from config import config


booted = Event()            # 0 - hier kann unterschieden werden ob das System schon an war oder neu gebootet ist
connectToWlan = Event()     # 1 - Wird gesetzt wenn gerade versucht wird eine Internetverbindung aufzubauen
checkForUpdates = Event()   # 2 - Es wird gerade nach Updates gesucht
deliverWebServer = Event()  # 3 - Der Webserver zum eingeben von SSID und Password fürs Wlan ist gerade aktiv
updateFirmware = Event()    # 4 - Die Firmware wird gerade aktualisiert
waitToCheck = Event()       # 5 - Es wird gerade gewartet um später nach Updates zu suchen

wlan_connected = Event()
wlan_connected_timeout = Event()


def connect_to_wlan(wlan):
    wlan.active(True)
    wlan.config(hostname=config['device_name'])
    if not wlan.isconnected():
        print('Connecting to network ', config['ssid'], '...')
        try:
            wlan.connect(config['ssid'], config['ssid_key'])
        except OSError:
            wlan.active(False)
            wlan.active(True)
            wlan.connect(config['ssid'], config['ssid_key'])


class UpdateStateMachine:
    def __init__(self):
        pass
    
    async def boot_device(self):
        # state 0
        booted.set()

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
    wlan = network.WLAN(network.WLAN.IF_STA)
    connect_to_wlan(wlan)
    

if __name__ == '__main__':
    main()