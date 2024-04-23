import time
from machine import Pin
from machine import Timer
from machine import RTC
from neopixel import NeoPixel

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


class Matrix:
    def __init__(self, row_pins):
        self.rows = self._get_rows(row_pins)

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

    def show_word(self, word, color=[150, 150, 150]):
        for led in word:
            self._set_led(led[1], led[0], color)

    def show_words(self, word_list, color=[150, 150, 150]):
        for word in word_list:
            self.show_word(word, color=color)

    def clear_word(self, word):
        for led in word:
            self._set_led(led[1], led[0], color=[0, 0, 0])

    def clear_words(self, word_list):
        for word in word_list:
            self.show_word(word, color=[0, 0, 0])

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
            self.show_word(NUMBERS[0])
        else:
            self.show_word(NUMBERS[hour])

    def _show_minute(self, minute):
        if minute < 5:
            self.clear_words([FÜNF_2, VOR])
            self.show_word(UHR)
        elif minute >= 5 and minute < 10:
            self.clear_word(UHR)
            self.show_words([FÜNF_2, NACH])
        elif minute >= 10 and minute < 15:
            self.clear_word(FÜNF_2)
            self.show_words([ZEHN_2, NACH])
        elif minute >= 15 and minute < 20:
            self.clear_word(ZEHN_2)
            self.show_words([VIERTEL, NACH])
        elif minute >= 20 and minute < 25:
            self.clear_word(VIERTEL)
            self.show_words([ZWANZIG, NACH])
        elif minute >= 25 and minute < 30:
            self.clear_words([ZWANZIG, NACH])
            self.show_words([FÜNF_2, VOR, HALB])
        elif minute >= 30 and minute < 35:
            self.clear_words([FÜNF_2, VOR])
            self.show_word(HALB)
        elif minute >= 35 and minute < 40:
            self.show_words([FÜNF_2, NACH, HALB])
        elif minute >= 40 and minute < 45:
            self.clear_words([FÜNF_2, NACH, HALB])
            self.show_words([ZWANZIG, VOR])
        elif minute >= 45 and minute < 50:
            self.clear_words([ZWANZIG, HALB])
            self.show_words([VIERTEL, VOR])
        elif minute >= 50 and minute < 55:
            self.clear_word(VIERTEL)
            self.show_words([ZEHN_2, VOR])
        elif minute >= 55 and minute != 0:
            self.clear_word(ZEHN_2)
            self.show_words([FÜNF_2, VOR])
        
    def show_time(self, hour, minute):
        if minute >= 25:
            hour = hour + 1
        self.show_words([ES, IST])
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

    def datetime(self):
        return (self.year, self.month, self.day, self.weekday, self.hour, self.minute, self.second, self.microsecond)


def main():
    matrix = Matrix(ROW_PINS)
    matrix.clear()

    rtc = RTCmock(2024, 4, 23, 0, 12, 0, 0, 0)
    rtc.change_speed(100)
    rtc.start()

    # real_rtc = RTC()
    # real_rtc.datetime((2024, 4, 23, 0, 12, 42, 0, 0))

    while(True):
        current_datetime = rtc.datetime()
        print(current_datetime[HOUR], ":", current_datetime[MINUTE])
        matrix.show_time(current_datetime[HOUR], current_datetime[MINUTE])
        time.sleep(1)


if __name__ == '__main__':
    main()
