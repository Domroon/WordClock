from neopixel import NeoPixel
from machine import Pin


# COLORS
WHITE = [150, 150, 150]
RED = [150, 0, 0]
GREEN = [0, 150, 0]
BLUE = [0, 0, 150]
YELLOW = [150, 150, 0]

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


class Matrix:
    def __init__(self):
        self.rows: list = self._get_rows(ROW_PINS)
        self.dots: NeoPixel = NeoPixel(Pin(DOTS_PIN, Pin.OUT), 4)

    def _get_rows(self, row_pins):
        rows = []
        for pin in row_pins:
          rows.append(NeoPixel(Pin(pin, Pin.OUT), 11))
        return rows

    def set_led(self, x, y, color):
        self.rows[x][y] = color
        self.rows[x].write()

    def show_word(self, word, color, rainbow=False):
        if rainbow:
            colors = [RED, GREEN, BLUE, YELLOW]
            i = 0
            for led in word:
                if i == len(colors):
                    i = 0
                self.set_led(led[1], led[0], colors[i])
                i = i + 1
        else:
            for led in word:
                self.set_led(led[1], led[0], color)

    def show_words(self, word_list, color, rainbow=False):
        for word in word_list:
            self.show_word(word, color, rainbow=rainbow)

    def clear_word(self, word):
        for led in word:
            self.set_led(led[1], led[0], color=[0, 0, 0])

    def clear_words(self, word_list):
        for word in word_list:
            self.show_word(word, color=[0, 0, 0])

    def clear(self):
        for row in self.rows:
            row.fill([0, 0, 0])
            row.write()


class TimeScreen:
    def __init__(self, matrix):
        self.matrix: Matrix = matrix
        self.word_color: list[int] = WHITE
        self.dots_color: list[int] = WHITE
        self.rainbow: bool = False

    def _show_hour(self, hour, minute):
        if(hour > 12):
            hour = hour - 12
        if hour == 0:
            hour = 12

        if hour == 1:
            self.matrix.clear_word(NUMBERS[12])
        else:
            self.matrix.clear_word(NUMBERS[hour-1])

        if minute < 5 and hour == 1:
            self.matrix.clear_word(NUMBERS[1])
            self.matrix.show_word(NUMBERS[0], self.word_color, rainbow=self.rainbow)
        else:
            self.matrix.show_word(NUMBERS[hour], self.word_color, rainbow=self.rainbow)

    def _show_minute(self, minute):
        if minute % 5 == 0:
            self.matrix.dots.fill([0, 0, 0])
        elif minute % 5 == 1:
            self.matrix.dots[0] = self.dots_color
        elif minute % 5 == 2:
            self.matrix.dots[0] = self.dots_color
            self.matrix.dots[1] = self.dots_color
        elif minute % 5 == 3:
            self.matrix.dots[0] = self.dots_color
            self.matrix.dots[1] = self.dots_color
            self.matrix.dots[2] = self.dots_color
        elif minute % 5 == 4:
            self.matrix.dots[0] = self.dots_color
            self.matrix.dots[1] = self.dots_color
            self.matrix.dots[2] = self.dots_color
            self.matrix.dots[3] = self.dots_color
        self.matrix.dots.write()

        if minute < 5:
            self.matrix.clear_words([FÜNF_2, VOR])
            self.matrix.show_word(UHR, self.word_color)
        elif minute >= 5 and minute < 10:
            self.matrix.clear_word(UHR)
            self.matrix.show_words([FÜNF_2, NACH], self.word_color)
        elif minute >= 10 and minute < 15:
            self.matrix.clear_word(FÜNF_2)
            self.matrix.show_words([ZEHN_2, NACH], self.word_color)
        elif minute >= 15 and minute < 20:
            self.matrix.clear_word(ZEHN_2)
            self.matrix.show_words([VIERTEL, NACH], self.word_color)
        elif minute >= 20 and minute < 25:
            self.matrix.clear_word(VIERTEL)
            self.matrix.show_words([ZWANZIG, NACH], self.word_color)
        elif minute >= 25 and minute < 30:
            self.matrix.clear_words([ZWANZIG, NACH])
            self.matrix.show_words([FÜNF_2, VOR, HALB], self.word_color)
        elif minute >= 30 and minute < 35:
            self.matrix.clear_words([FÜNF_2, VOR])
            self.matrix.show_word(HALB, self.word_color)
        elif minute >= 35 and minute < 40:
            self.matrix.show_words([FÜNF_2, NACH, HALB], self.word_color)
        elif minute >= 40 and minute < 45:
            self.matrix.clear_words([FÜNF_2, NACH, HALB])
            self.matrix.show_words([ZWANZIG, VOR], self.word_color)
        elif minute >= 45 and minute < 50:
            self.matrix.clear_words([ZWANZIG, HALB])
            self.matrix.show_words([VIERTEL, VOR], self.word_color)
        elif minute >= 50 and minute < 55:
            self.matrix.clear_word(VIERTEL)
            self.matrix.show_words([ZEHN_2, VOR], self.word_color)
        elif minute >= 55 and minute != 0:
            self.matrix.clear_word(ZEHN_2)
            self.matrix.show_words([FÜNF_2, VOR], self.word_color)
        
    def show_time(self, hour, minute):
        if minute >= 25:
            hour = hour + 1
        self.matrix.show_words([ES, IST], self.word_color)
        self._show_hour(hour, minute)
        self._show_minute(minute)

    def clear(self):
        self.matrix.clear()


class UserInfoScreen:
    def __init__(self, matrix):
        self.matrix: Matrix = matrix

    def show_set_mode(self):
        self.matrix.set_led(9, 1, YELLOW)
        self.matrix.set_led(9, 2, YELLOW)
        self.matrix.set_led(8, 4, YELLOW)
        self.matrix.set_led(8, 5, YELLOW)
        self.matrix.set_led(8, 6, YELLOW)
    
    def show_empty_battery(self):
        self.matrix.set_led(0, 0, RED)
        self.matrix.set_led(4, 3, RED)

    def clear(self):
        self.matrix.clear()