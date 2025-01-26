from asyncio import sleep, create_task, run, get_event_loop
from screen import TimeScreen, Matrix


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
    time_screen.matrix.clear()
    minutes = 0
    while True:
        time_screen.show_time(2, minutes)
        minutes = minutes + 1
        await sleep(1)


async def main():
    matrix = Matrix()
    create_task(print_hello_1())
    create_task(print_hello_2())
    create_task(show_time(matrix))

    event_loop = get_event_loop()
    event_loop.run_forever()


run(main())