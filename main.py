from machine import Pin
from neopixel import NeoPixel


ES =        [[0, 0], [1,0]]
IST =       [[3, 0], [4, 0], [5, 0]]
FÜNF =      [[7, 0], [8, 0], [9, 0], [10, 0]]
ZEHN =      [[0, 1], [1, 1], [2, 1], [3, 1]]
ZWANZIG =   [[4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1]]
DREI =      [[0, 2], [1, 2], [2, 2], [3, 2]]
VIERTEL =   [[4, 2], [5, 2], [6, 2], [7, 2], [8, 2], [9, 2], [10, 2]]
NACH =      [[2, 3], [3, 3], [4, 3], [5, 3]]
VOR =       [[6, 3], [7, 3], [8, 3]]
HALB =      [[0, 4], [1, 4], [2, 4], [3, 4]]
ZWÖLF =     [[5, 4], [6, 4], [7, 4], [8, 4]]
ZWEI  =     [[0, 5], [1, 5], [2, 5], [3, 5]]
SIEBEN=     [[5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5]]
DREI_2=     [[1, 6], [2, 6], [3, 6], [4, 6]]
FÜNF_2=     [[7, 6], [8, 6], [9, 6], [10, 6]]
ELF =       [[0, 7], [1, 7], [2, 7]]
NEUN =      [[3, 7], [4, 7], [5, 7], [6, 7]]
VIER =      [[7, 7], [8, 7], [9, 7], [10, 7]]
ACHT =      [[1, 8], [2, 8], [3, 8], [4, 8]]
ZEHN_2 =    [[5, 8], [6, 8], [7, 8], [8, 8]]
SECHS =     [[1, 9], [2, 9], [3, 9], [4, 9], [5, 9]]
UHR =       [[7, 9], [8, 9], [9, 9]]

ROW_PINS = [21, 19, 18, 5, 17, 16, 4, 0, 2, 15]


class Matrix:
    def __init__(self, row_pins):
        self._row_pins = row_pins
        self.rows = self._get_pins(self._row_pins)

    def _get_pins(self, row_pins):
        rows = []
        for pin in row_pins:
          rows.append(NeoPixel(Pin(pin, Pin.OUT), 11))
        return rows

    def _set_led(self, x, y, color=[50, 50, 50]):
        self.rows[x][y] = color
        self.rows[x].write()


def main():
    matrix = Matrix(ROW_PINS)
    matrix._set_led(0, 0)
    matrix._set_led(1, 1)
    matrix._set_led(2, 2)


if __name__ == '__main__':
    main()
