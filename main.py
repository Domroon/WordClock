import network
from asyncio import sleep, create_task, run, get_event_loop, Event

from screen import TimeScreen, Matrix, AnimationScreen, BLUE


wlan_connected = Event()
wlan_connected_timeout = Event()


SSID = 'AlphaCentauri'
SSID_KEY = 'vhuj7240'


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
        if wlan_connected.is_set():
            wlan_config = wlan.ifconfig()
            ip_adress = wlan_config[0]
            hostname = wlan.config('hostname')
            print('Connected to', SSID, 'as', hostname,'with', ip_adress)
        if wlan_connected_timeout.is_set():
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
        if wlan_connected.is_set() or wlan_connected_timeout.is_set():
            break
        if frame == 7:
            frame = 0
        animation_screen.show_wait_line(frame, BLUE)
        frame = frame + 1
        await sleep(0.1)

async def show_sucess_animation(animation_screen):
    frame = 0
    while True:
        if frame == 11 or wlan_connected_timeout.is_set():
            break
        if wlan_connected.is_set():
            animation_screen.show_success_animation(frame)
            frame = frame + 1
        await sleep(0.1)

async def show_fail_animation(animation_screen):
    frame = 0
    while True:
        if frame == 11:
            break
        if wlan_connected_timeout.is_set():
            animation_screen.show_fail_animation(frame)
            frame = frame + 1
        await sleep(0.1)


# network coroutines

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


async def main():
    matrix = Matrix()
    animation_screen = AnimationScreen(matrix)
    wlan = network.WLAN(network.WLAN.IF_STA)

    matrix.clear()

    # general Tasks
    create_task(print_alive())
    create_task(log(wlan))

    # wlan tasks
    connect_to_wlan(wlan)
    create_task(set_wlan_connected_timeout_event())
    create_task(set_wlan_connected_event(wlan))

    # show tasks

    # create_task(network_found_test(matrix))
    create_task(show_wait_animation(animation_screen))
    create_task(show_sucess_animation(animation_screen))
    create_task(show_fail_animation(animation_screen))
    # create_task(show_time(matrix))

    event_loop = get_event_loop()
    event_loop.run_forever()


run(main())