import time
from random import randint

from machine import Pin, SoftI2C, TouchPad
from machine import Timer
from machine import RTC
from neopixel import NeoPixel

from networking import Client
from networking import download_json_file, LINK
import logging
from logging import Logger
from ds3231 import DS3231

# COLORS
WHITE = [150, 150, 150]
RED = [150, 0, 0]
GREEN = [0, 150, 0]
BLUE = [0, 0, 150]
YELLOW = [255, 255, 0]

# Static Variables for RTC
YEAR = 0
MONTH = 1
DAY = 2
HOUR = 4
MINUTE = 5
SECOND = 6

# Always on
ES =        [[0, 0], [1,0]]
IST =       [[3, 0], [4, 0], [5, 0]]

# Numbers for before/after whole, half and quarter 
FÜNF_2 =      [[7, 0], [8, 0], [9, 0], [10, 0]]
ZEHN_2 =      [[0, 1], [1, 1], [2, 1], [3, 1]]
ZWANZIG =   [[4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1]]
DREI_2 =      [[0, 2], [1, 2], [2, 2], [3, 2]]

# Quarter, Half, Before, After
VIERTEL =   [[4, 2], [5, 2], [6, 2], [7, 2], [8, 2], [9, 2], [10, 2]]
NACH =      [[2, 3], [3, 3], [4, 3], [5, 3]]
VOR =       [[6, 3], [7, 3], [8, 3]]
HALB =      [[0, 4], [1, 4], [2, 4], [3, 4]]

# Numbers
NUMBERS =     {12: [[5, 4], [6, 4], [7, 4], [8, 4], [9, 4]],
                2: [[0, 5], [1, 5], [2, 5], [3, 5]],
                1: [[2, 5], [3, 5], [4, 5], [5, 5]],
                0: [[2, 5], [3, 5], [4, 5]],
                7: [[5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5]],
                3: [[1, 6], [2, 6], [3, 6], [4, 6]],
                5: [[7, 6], [8, 6], [9, 6], [10, 6]],
                11: [[0, 7], [1, 7], [2, 7]],
                9: [[3, 7], [4, 7], [5, 7], [6, 7]],
                4: [[7, 7], [8, 7], [9, 7], [10, 7]],
                8: [[1, 8], [2, 8], [3, 8], [4, 8]],
                10: [[5, 8], [6, 8], [7, 8], [8, 8]],
                6: [[1, 9], [2, 9], [3, 9], [4, 9], [5, 9]]}

# For whole hour
UHR =       [[7, 9], [8, 9], [9, 9]]

ROW_PINS = [21, 19, 18, 5, 17, 16, 4, 0, 2, 15]

DOTS_PIN = 25

TOUCH_PAD = 27

logger = Logger(logging.DEBUG)

class Matrix:
    def __init__(self, row_pins, word_color, dots_color):
        self.rows = self._get_rows(row_pins)
        self.word_color = word_color
        self.dots_color = dots_color
        self.dots = NeoPixel(Pin(DOTS_PIN, Pin.OUT), 4)

    def _get_rows(self, row_pins):
        rows = []
        for pin in row_pins:
          rows.append(NeoPixel(Pin(pin, Pin.OUT), 11))
        return rows

    def _set_led(self, x, y, color):
        self.rows[x][y] = color
        self.rows[x].write()

    def clear(self):
        for row in self.rows:
            row.fill([0, 0, 0])
            row.write()

    def show_word(self, word, color):
        for led in word:
            self._set_led(led[1], led[0], color)

    def show_words(self, word_list, color):
        for word in word_list:
            self.show_word(word, color)

    def clear_word(self, word):
        for led in word:
            self._set_led(led[1], led[0], color=[0, 0, 0])

    def clear_words(self, word_list):
        for word in word_list:
            self.show_word(word, color=[0, 0, 0])

    def show_set_mode(self):
        self._set_led(9, 1, YELLOW)
        self._set_led(9, 2, YELLOW)
        self._set_led(8, 4, YELLOW)
        self._set_led(8, 5, YELLOW)
        self._set_led(8, 6, YELLOW)

    def _show_hour(self, hour, minute):
        if(hour > 12):
            hour = hour - 12
        if hour == 0:
            hour = 12

        if hour == 1:
            self.clear_word(NUMBERS[12])
        else:
            self.clear_word(NUMBERS[hour-1])

        if minute < 5 and hour == 1:
            self.clear_word(NUMBERS[1])
            self.show_word(NUMBERS[0], self.word_color)
        else:
            self.show_word(NUMBERS[hour], self.word_color)

    def _show_minute(self, minute):
        if minute % 5 == 0:
            self.dots.fill([0, 0, 0])
        elif minute % 5 == 1:
            self.dots[0] = self.dots_color
        elif minute % 5 == 2:
            self.dots[0] = self.dots_color
            self.dots[1] = self.dots_color
        elif minute % 5 == 3:
            self.dots[0] = self.dots_color
            self.dots[1] = self.dots_color
            self.dots[2] = self.dots_color
        elif minute % 5 == 4:
            self.dots[0] = self.dots_color
            self.dots[1] = self.dots_color
            self.dots[2] = self.dots_color
            self.dots[3] = self.dots_color
        self.dots.write()

        if minute < 5:
            self.clear_words([FÜNF_2, VOR])
            self.show_word(UHR, self.word_color)
        elif minute >= 5 and minute < 10:
            self.clear_word(UHR)
            self.show_words([FÜNF_2, NACH], self.word_color)
        elif minute >= 10 and minute < 15:
            self.clear_word(FÜNF_2)
            self.show_words([ZEHN_2, NACH], self.word_color)
        elif minute >= 15 and minute < 20:
            self.clear_word(ZEHN_2)
            self.show_words([VIERTEL, NACH], self.word_color)
        elif minute >= 20 and minute < 25:
            self.clear_word(VIERTEL)
            self.show_words([ZWANZIG, NACH], self.word_color)
        elif minute >= 25 and minute < 30:
            self.clear_words([ZWANZIG, NACH])
            self.show_words([FÜNF_2, VOR, HALB], self.word_color)
        elif minute >= 30 and minute < 35:
            self.clear_words([FÜNF_2, VOR])
            self.show_word(HALB, self.word_color)
        elif minute >= 35 and minute < 40:
            self.show_words([FÜNF_2, NACH, HALB], self.word_color)
        elif minute >= 40 and minute < 45:
            self.clear_words([FÜNF_2, NACH, HALB])
            self.show_words([ZWANZIG, VOR], self.word_color)
        elif minute >= 45 and minute < 50:
            self.clear_words([ZWANZIG, HALB])
            self.show_words([VIERTEL, VOR], self.word_color)
        elif minute >= 50 and minute < 55:
            self.clear_word(VIERTEL)
            self.show_words([ZEHN_2, VOR], self.word_color)
        elif minute >= 55 and minute != 0:
            self.clear_word(ZEHN_2)
            self.show_words([FÜNF_2, VOR], self.word_color)
        
    def show_time(self, hour, minute):
        if minute >= 25:
            hour = hour + 1
        self.show_words([ES, IST], self.word_color)
        self._show_hour(hour, minute)
        self._show_minute(minute)


# add the the same functionality like the machine.RTC class
class RTCmock:
    def __init__(self, year, month, day, weekday, hour, minute, second, microsecond):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.day = day
        self.weekday = weekday
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.timer = Timer(0)
        self.speed = 1

    def start(self):
        self.timer.init(period=int(self.speed*1000), callback=self._tick)

    def change_speed(self, multiplier):
        self.speed = 1 / multiplier

    def _tick(self, timer_obj):
        self.second = self.second + 1
        if self.second > 59:
            self.minute = self.minute + 1
            self.second = 0
        if self.minute > 59:
            self.hour = self.hour + 1
            self.minute = 0
        if self.hour > 23:
            self.hour = 0
        # print(self.hour, ":", self.minute, ":", self.second)

    def datetime(self, datetime_data=None):
        if datetime_data == None:
            return (self.year, self.month, self.day, self.weekday, self.hour, self.minute, self.second, self.microsecond)
        self.year = datetime_data[0]
        self.month = datetime_data[1]
        self.day = datetime_data[2]
        self.weekday = datetime_data[3]
        self.hour = datetime_data[4]
        self.minute = datetime_data[5]
        self.second = datetime_data[6]
        self.microseconds = datetime_data[7]


class Timekeeper():
    def __init__(self, ds3231):
        self.ds3231 = ds3231
        
    def set_by_cli(self):
        print("You are in the clock settings. Do you want to change the time (y/n)?")
        while True:
            user_input = input()
            if user_input == "y":
                year = int(input("Enter Year: "))
                month = int(input("Enter Month: "))
                mday = int(input("Enter Day: "))
                hour = int(input("Enter Hour (24h format): "))
                minute = int(input("Enter Minute: "))
                second = int(input("Enter Second: ")) # Optional
                print("Enter Weekday (0-6)")
                print("0 - Sunday")
                print("1 - Monday")
                print("2 - Thuesday")
                print("3 - Wednesday")
                print("4 - Thursday")
                print("5 - Friday")
                print("6 - Saturday")
                weekday = int(input())  # Optional
                input("Press Enter to set the Time...")

                datetime = (year, month, mday, hour, minute, second, weekday)
                self.ds3231.datetime(datetime)
                break
            elif user_input == "n":
                print("no")
                break
            else:
                print("Wrong Input. Enter 'y' for yes ot 'n' for no.")

    def get_datetime(self):
        return self.ds3231.datetime()
    
    def is_time_lost(self):
        if(self.get_datetime()[0] == 2000):
            return True
        return False


class DS3231Mock:
    def __init__(self):
        self.year = 2000        
        self.month = 1
        self.day = 1
        self.weekday = 5
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.microseconds = 0        

    def datetime(self, datetime_data=None):
        if datetime_data == None:
            return (self.year, self.month, self.day, self.weekday, self.hour, self.minute, self.second, self.microseconds)
        self.year = datetime_data[0]
        self.month = datetime_data[1]
        self.day = datetime_data[2]
        self.weekday = datetime_data[3]
        self.hour = datetime_data[4]
        self.minute = datetime_data[5]
        self.second = datetime_data[6]
        self.microseconds = datetime_data[7]


class Animation:
    def __init__(self, matrix):
        self.matrix = matrix
        self.qty_col = 11
        self.qty_row = 10
        self.words = [
            ES, IST, FÜNF_2, ZEHN_2, ZWANZIG, DREI_2,
            VIERTEL, NACH, VOR, HALB, UHR
        ]
        self._add_numbers()

    def _add_numbers(self):
        for i in range(12):
            self.words.append(NUMBERS[i])

    def random_words(self, duration, on_dura=0.2, random_color=False):
        duration = duration / on_dura
        loops = 0
        color = WHITE
        colors = [WHITE, RED, GREEN, BLUE]
        while True:
            if loops == duration:
                break
            if random_color:
                rand_num = randint(0, len(colors)-1)
                color = colors[rand_num]
            rand_num = randint(0, len(self.words)-1)
            self.matrix.show_word(self.words[rand_num], color)
            time.sleep(on_dura)
            self.matrix.clear_word(self.words[rand_num])
            loops = loops + 1


def set_rtc(rtc, timeinfo_json):
    logger.info("Set RTC:")
    timeinfo = {}
    timeinfo['year'] = timeinfo_json['year']
    timeinfo['month'] = timeinfo_json['month']
    timeinfo['day'] = timeinfo_json['day']
    timeinfo['hour'] = timeinfo_json['hour']
    timeinfo['minute'] = timeinfo_json['minute']
    timeinfo['second'] = timeinfo_json['seconds']
    rtc.datetime((timeinfo['year'], 
                  timeinfo['month'], 
                  timeinfo['day'], 
                  0, 
                  timeinfo['hour'], timeinfo['minute'], timeinfo['second'], 
                  0))
    logger.info(timeinfo)
    logger.info("RTC Output: ")
    logger.info(rtc.datetime())


def set_rtc_with_timekeeper(rtc, timekeeper):
    logger.info("Read datetime from timekeeper DS3231...")
    rtc.datetime(timekeeper.get_datetime())
    logger.info("Set internal RTC datetime to:")
    logger.info("Year | Month | Day | Weekday | Hour | Minute | Second | Microseconds")
    logger.info(rtc.datetime())


def read_settings():
    conf = {}
    with open("settings.conf", 'r') as file:
        for line in file:
            line = line.split('=')
            line[1] = line[1].replace('\n', '')
            conf[line[0]] = line[1]
    return conf


# def execute_tests():
#     # preparing objects for th tests
#     touch = TouchPad(Pin(TOUCH_PAD))
#     matrix = Matrix(ROW_PINS, [150, 150, 150])
#     rtc = RTCmock(2024, 9, 11, 0, 15, 25, 0, 0)
#     rtc.change_speed(100)
#     rtc.start()
#     ani = Animation(matrix)
#     matrix.clear()
#     ds3231_mock = DS3231Mock()
#     timekeeper_mock = Timekeeper(ds3231_mock)
#     i2c = SoftI2C(sda=Pin(32), scl=Pin(33))
#     ds3231 = DS3231(i2c)
#     timekeeper = Timekeeper(ds3231)


class Test:
    def __init__(self):
        self.touch = TouchPad(Pin(TOUCH_PAD))
        self.matrix = Matrix(ROW_PINS, WHITE, WHITE)
        self.rtc_mock = RTCmock(2024, 9, 11, 0, 15, 25, 0, 0)
        self.rtc = RTC() 
        # rtc_mock.change_speed(100)
        # rtc_mock.start()
        self.ani = Animation(self.matrix)
        # matrix.clear()
        self.ds3231_mock = DS3231Mock()
        self.timekeeper_mock = Timekeeper(self.ds3231_mock)
        self.i2c = SoftI2C(sda=Pin(32), scl=Pin(33))
        self.ds3231 = DS3231(self.i2c)
        self.timekeeper = Timekeeper(self.ds3231)
        self.test_list = [
            self.test_is_time_lost_true(self.timekeeper),
            self.test_is_time_lost_false(self.timekeeper),
            self.test_user_check_correct_times()
        ]
    
    def get_test_result_string(self, result):
        if result:
            return "OK"
        return "FAIL"
    
    def test_is_time_lost_true(self, timekeeper):
        print("Remove the battery from the Timekeeper then disconnect the device from the power supply...")
        input("If you have already removed the battery: Press enter...")
        if self.timekeeper.is_time_lost() == True:
            return "OK \t test_is_time_lost_true"
        return "FAIL \t test_is_time_lost_true"

    def test_is_time_lost_false(self, timekeeper):
        self.timekeeper.set_by_cli()
        if self.timekeeper.is_time_lost() == False:
            return "OK \t test_is_time_lost_false"
        return "FAIL \t test_is_time_lost_false"
    
    def test_user_check_correct_times(self):
        print("The time from 11 a.m. to 1 p.m. will now be displayed in rapid succession. Make sure that everything is correct.")
        input("When you are ready press enter...")
        print("Currently showing the time...")
        self.rtc_mock.datetime((2024, 9, 11, 0, 11, 0, 0, 0))
        self.rtc_mock.change_speed(50)
        self.rtc_mock.start()
        self.matrix.clear()
        while True:
            current_datetime = self.rtc_mock.datetime()
            if current_datetime[4] == 13:
                break
            self.matrix.show_time(current_datetime[HOUR], current_datetime[MINUTE])
            time.sleep(1)
        while True:
            user_input = input("Were all times correct? y/n")
            if user_input == "y":
                return "OK \t test_user_check_correct_times"
            elif user_input == "n":
                return "FAIL \t test_user_check_correct_times"
            else:
                print("Wrong Input. Enter 'y' for yes ot 'n' for no.")

    def run_tests(self):
        results = []
        error_counter = 0
        for test in self.test_list:
            print(test)
            results.append(test)

        for result in results:
            if "FAIL" in result:
                error_counter = error_counter + 1

        if error_counter == 0:
            print("All tests were successful :)")
        else:
            print(error_counter, " test(s) failed :(")

        input('All tests are executed. Press enter to execute the normal mode...')
        input



def main():
    conf = read_settings()
    logger.info('Read configuration....')
    logger.info('Configuration:')
    print(conf)
    if conf['enable_test_mode'] == 'True':
        logger.info('Run Tests')
        tests = Test()
        tests.run_tests()

    touch = TouchPad(Pin(TOUCH_PAD))
    matrix = Matrix(ROW_PINS, WHITE, WHITE)
    rtc = RTC()        
    ani = Animation(matrix)
    matrix.clear()
    ani.random_words(2, random_color=True)
    i2c = SoftI2C(sda=Pin(32), scl=Pin(33))
    ds3231 = DS3231(i2c)
    timekeeper = Timekeeper(ds3231)

    set_rtc_with_timekeeper(rtc, timekeeper)

    matrix.clear()

    while(True):
        if touch.read() <= 100:
            matrix.clear()
            matrix.show_set_mode()
            timekeeper.set_by_cli()
            rtc.datetime(timekeeper.get_datetime())
            matrix.clear()
        current_datetime = rtc.datetime()
        matrix.show_time(current_datetime[HOUR], current_datetime[MINUTE])
        time.sleep(1)


if __name__ == '__main__':
    main()
