from asyncio import sleep, create_task, run, get_event_loop
from matrix import Matrix


async def print_hello_1():
    while True:
        print("Hello 1")
        await sleep(2)


async def print_hello_2():
    while True:
        print("Hello 2")
        await sleep(1)


async def show_time():
    matrix = Matrix()
    matrix.clear()
    minutes = 0
    while True:
        matrix.show_time(2, minutes)
        minutes = minutes + 1
        await sleep(1)


async def main():
    create_task(print_hello_1())
    create_task(print_hello_2())
    create_task(show_time())

    event_loop = get_event_loop()
    event_loop.run_forever()


run(main())