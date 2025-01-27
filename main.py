from asyncio import sleep, create_task, run, get_event_loop, Event
from screen import TimeScreen, Matrix, AnimationScreen, BLUE

network_found = Event()

async def print_hello_1():
    while True:
        print("Hello 1")
        await sleep(2)


async def print_hello_2():
    while True:
        print("Hello 2")
        await sleep(1)


async def show_time(matrix):
    time_screen = TimeScreen(matrix)
    matrix.clear()
    minutes = 0
    while True:
        time_screen.show_time(2, minutes)
        minutes = minutes + 1
        await sleep(1)


async def show_wait_animation(matrix):
    animation_screen = AnimationScreen(matrix)
    matrix.clear()
    frame = 0
    while True:
        if network_found.is_set():
            break
        if frame == 7:
            frame = 0
        animation_screen.show_wait_line(frame, BLUE)
        frame = frame + 1
        await sleep(0.1)


async def network_found_test(matrix):
    i = 0
    while True:
        if i == 5:
            network_found.set()
            print("found network")
            create_task(show_time(matrix))
        i = i + 1
        await sleep(1)


async def main():
    matrix = Matrix()
    create_task(print_hello_1())
    create_task(print_hello_2())
    create_task(network_found_test(matrix))
    create_task(show_wait_animation(matrix))
    # create_task(show_time(matrix))

    event_loop = get_event_loop()
    event_loop.run_forever()


run(main())