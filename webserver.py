from machine import RTC

from microdot import Microdot
from microdot import send_file, redirect


app = Microdot()


@app.route('/html/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('html/' + path)


@app.route('/', methods=['GET', 'POST'])
def set_time(request):
    if request.method == 'POST':
        # add here function that reads the ssid and password 
        # and writes it into stored_networks.txt

        # date = request.form.get('date').split('-')
        # weekday = request.form.get('weekday')
        # time = request.form.get('time').split(':')

        # year = int(date[0])
        # month = int(date[1])
        # day = int(date[2])
        # weekday = int(weekday)
        # hour = int(time[0])
        # minute = int(time[1])
        
        # rtc = RTC()
        # rtc.datetime((year, month, day, weekday, hour, minute, 0, 0))
        # print("datetime:", rtc.datetime())
        return send_file('/html/success.html')
    return send_file('/html/index.html')


@app.route('/success', methods=['GET', 'POST'])
def success(request):
    return send_file('/html/success.html')


class WebServer:
    def __init__(self, logger, memory):
        self.log = logger
        self.memory = memory
        
    def start(self):
        self.memory.clean_ram()
        self.log.info('Start Webserver')
        try:
            app.run(port=80, debug=True)
        except OSError as e:
            self.log.warning(e)
        self.memory.clean_ram()
        self.log.info('Shutdown Webserver')