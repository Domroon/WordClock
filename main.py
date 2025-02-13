from machine import RTC
import network
from asyncio import sleep, create_task, run, get_event_loop, Event

import ntptime

from ds3231 import Timekeeper
from config import config
from screen import TimeScreen, Matrix, AnimationScreen, BLUE
import events


# Network Events

wlan_connected = Event()
wlan_connected_timeout = Event()

# Update StateMachine Events - es kann immer nur ein StateMachine Event aktiv sein, nie mehrere gleichzeitig (außer booted)

booted = Event()                # 0 - hier kann unterschieden werden ob das System schon an war oder neu gebootet ist
checkTimekeeperState = Event()  # 1 - Hier wird geprüft ob der Timekeeper eine valide Uhrzeit liefert
connectToWlan = Event()         # 2 - Wird gesetzt wenn gerade versucht wird eine Internetverbindung aufzubauen
checkForUpdates = Event()       # 3 - Es wird gerade nach Updates gesucht
deliverWebServer = Event()      # 4 - Der Webserver zum eingeben von SSID und Password fürs Wlan ist gerade aktiv
updateFirmware = Event()        # 5 - Die Firmware wird gerade aktualisiert
waitToCheck = Event()           # 6 - Es wird gerade gewartet um später nach Updates zu suchen

# Time Validation Events

time_set_by_internet = Event()
timekeeper_time_is_valid = Event()

# Screen Events - es kann immer nur ein Screen Event aktiv sein, nie mehrere gleichzeitig

showStartInfo = Event()         # Sollte einmal nach dem Start aktiv sein um zu zeigen ob der Timekeeper eine valide Zeit hat,
                                # ob Wlan verbunden ist und ob auf Updates geprüft werden konnte
                                # Erste LED zeigt grün oder rot (je nachdem ob Timekeeper valide ist)
                                # Zweite LED zeigt grün oder rot (je nachdem ob Internet verbunden)
                                # Dritte LED zeigt grün für Updates überprüft, es liegen keine neuen vor
                                # rot für es konnte nicht auf neue Updates geprüft werden und gelb für 
                                # es liegen neue Updates vor
showTime = Event()              # Sollte immer dann gesetzt werden wenn die Zeit angezeigt werden soll
showUpdateProgress = Event()    # Sollte angezeigt werden wenn gerade ein Update durchgeführt wird


class UpdateStateMachine:
    def __init__(self, timekeeper, wlan):
        self.state = 0
        self.timekeeper: Timekeeper = timekeeper
        self.wlan: network.WLAN = wlan
    
    async def boot_device(self):
        # state 0
        booted.set()
        self.state = 1

    async def check_timekeeper_state(self):
        # state 1
        checkTimekeeperState.set()
        if not(self.timekeeper.is_time_lost()):
            timekeeper_time_is_valid.set()
        else:
            timekeeper_time_is_valid.clear()
        self.state = 2
        checkTimekeeperState.clear()
        
    async def connect_to_wlan(self):
        # state 2
        connectToWlan.set()
        connect_to_wlan(self.wlan)
        while True:
            if wlan_connected_timeout.is_set() and booted.is_set():
                self.state = 4
                break
            if wlan_connected_timeout.is_set():
                self.state = 6
                break
            if wlan_connected.is_set():
                self.state = 3
                break
            await sleep(1)
        connectToWlan.clear()

    async def check_for_updates(self):
        # state 3
        checkForUpdates.set()
        # check udpdates here
        await sleep(5)
        checkForUpdates.clear()

    async def deliver_webserver(self):
        # state 4
        deliverWebServer.set()
        # deliver webserver here
        await sleep(5)
        deliverWebServer.clear()

    async def update_firmware(self):
        # state 5
        updateFirmware.set()
        # update firmware here
        await sleep(5)
        updateFirmware.clear()

    async def wait_to_check_updates(self):
        # state 6
        waitToCheck.set()
        # wait here
        await sleep(5)
        waitToCheck.clear()

    async def set_current_event(self):
        pass

    async def start(self):
        while True:
            print('UpdateStateMachine in state: ', self.state)
            if self.state == 0:
                create_task(self.boot_device())
            elif self.state == 1:
                create_task(self.check_timekeeper_state())
            elif self.state == 2:
                create_task(self.connect_to_wlan())
            elif self.state == 3:
                create_task(self.check_for_updates())
            elif self.state == 4:
                create_task(self.deliver_webserver())
            elif self.state == 5:
                create_task(self.update_firmware())
            elif self.state == 6:
                create_task(self.wait_to_check_updates())
            await sleep(1)


class TimeStateMachine:
    def __init__(self, timekeeper, rtc):
        self.state = 0
        self.first_run = True
        self.wait_time = 30
        self.timekeeper = timekeeper
        self.rtc = rtc

    async def check_wlan(self):
        # state 1
        if wlan_connected.is_set() and self.first_run:
            self.first_run = False
            self.state = 2
        elif wlan_connected.is_set():
            self.state = 3
        else:
            self.state = 4

    async def update_timekeeper(self):
        # state 2
        ntptime.set_timekeeper_time(self.timekeeper)
        print(f'Synced Timekeeper with ntp-server "{ntptime.host}"')
        print(f'Timekeeper-datetime: {self.timekeeper.get_datetime()}')
        self.state = 3
        await sleep(2)

    async def update_rtc(self):
        # state 3
        ntptime.set_rtc_time(self.rtc)
        print(f'Synced RTC with ntp-server "{ntptime.host}"')
        print(f'RTC-datetime: {self.rtc.datetime()}')
        self.state = 4
        await sleep(2)

    async def wait_for_next_check(self):
        # state 4
        await sleep(self.wait_time)
        self.state = 1

    async def start(self):
        self.state = 1
        while True:
            print('TimeStateMachine state: ', self.state)
            if self.state == 1:
                create_task(self.check_wlan())
            elif self.state == 2:
                create_task(self.update_timekeeper())
            elif self.state == 3:
                create_task(self.update_rtc())
            elif self.state == 4:
                create_task(self.wait_for_next_check())
            await sleep(1)


# general coroutines and functions

async def print_alive():
    while True:
        print("Alive")
        await sleep(2)

def read_config():
    pass

async def log(wlan):
    # get all events and log whats happen
    # after the event is logged it should reset? -> maybe bad idea :D it should only reset by the coroutine that set it
    while True:
        if events.wlan_connected.is_set():
            wlan_config = wlan.ifconfig()
            ip_adress = wlan_config[0]
            hostname = wlan.config('hostname')
            print('Connected to', config['ssid'], 'as', hostname,'with', ip_adress)
        if events.wlan_connected_timeout.is_set():
            print('Wlan connected timeout')
        await sleep(1)


# show on screen coroutines 
async def show_time(matrix):
    time_screen = TimeScreen(matrix)
    matrix.clear()
    minutes = 0
    while True:
        time_screen.show_time(2, minutes)
        minutes = minutes + 1
        await sleep(1)

async def show_wait_animation(animation_screen):
    frame = 0
    while True:
        if events.wlan_connected.is_set() or events.wlan_connected_timeout.is_set():
            break
        if frame == 7:
            frame = 0
        animation_screen.show_wait_line(frame, BLUE)
        frame = frame + 1
        await sleep(0.1)

async def show_sucess_animation(animation_screen):
    frame = 0
    while True:
        if frame == 11 or events.wlan_connected_timeout.is_set():
            break
        if events.wlan_connected.is_set():
            animation_screen.show_success_animation(frame)
            frame = frame + 1
        await sleep(0.1)

async def show_fail_animation(animation_screen):
    frame = 0
    while True:
        if frame == 11:
            break
        if events.wlan_connected_timeout.is_set():
            animation_screen.show_fail_animation(frame)
            frame = frame + 1
        await sleep(0.1)

async def show_network_connection_status(animation_screen):
    while True:
        if events.wlan_connected.is_set():
            animation_screen.show_network_connected_dot()
        if events.wlan_connected_timeout.is_set():
            animation_screen.show_network_not_connected_dot()
        await sleep(0.1)

# network coroutines

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

async def set_wlan_connected_event(wlan):
    while True:
        if wlan.isconnected():
            wlan_connected.set()
        else:
            wlan_connected.clear()
        await sleep(5)

async def set_wlan_connected_timeout_event():
    wlan_connected_timeout.clear()
    timer = 0
    max_time = 10
    while True:
        if wlan_connected.is_set():
            wlan_connected_timeout.clear()
            timer = 0
        if timer >= max_time:
            wlan_connected_timeout.set()
            await sleep(5)
            wlan_connected_timeout.clear()
            timer = 0
        timer = timer + 1
        await sleep(1)


# from ds3231 import Timekeeper
# rtc = RTC()
# timekeeper = Timekeeper(rtc)
# print(timekeeper.is_time_lost())
# print("test")

async def main():
    rtc = RTC() 
    matrix = Matrix()
    animation_screen = AnimationScreen(matrix)
    wlan = network.WLAN(network.WLAN.IF_STA)
    timekeeper = Timekeeper(rtc)

    update_state_machine = UpdateStateMachine(timekeeper, wlan)
    time_state_machine = TimeStateMachine(timekeeper, rtc)

    matrix.clear()

    # general Tasks
    create_task(print_alive())
    create_task(log(wlan))
    create_task(time_state_machine.start())

    # wlan tasks
    connect_to_wlan(wlan)
    create_task(set_wlan_connected_timeout_event())
    create_task(set_wlan_connected_event(wlan))

    # state machine tasks
    create_task(update_state_machine.start())

    # show tasks
    # create_task(show_wait_animation(animation_screen))
    # create_task(show_network_connection_status(animation_screen))

    event_loop = get_event_loop()
    event_loop.run_forever()


run(main())