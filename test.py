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