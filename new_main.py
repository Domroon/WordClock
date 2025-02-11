import network
from asyncio import Event

from config import config


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
        events.booted.set()

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