from machine import RTC
from main import Timekeeper

from microdot import Microdot
from microdot import send_file
from networking import change_stored_networks


app = Microdot()


@app.route('/html/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('html/' + path)


@app.get('/')
def index(request):
    return send_file('/html/index.html')


@app.route('/time', methods=['GET', 'POST'])
def set_time(request):
    if request.method == 'POST':
        date = request.form.get('date').split('-')
        weekday = request.form.get('weekday')
        time = request.form.get('time').split(':')

        year = int(date[0])
        month = int(date[1])
        day = int(date[2])
        weekday = int(weekday)
        hour = int(time[0])
        minute = int(time[1])
        
        rtc = RTC()
        rtc.datetime((year, month, day, weekday, hour, minute, 0, 0))
        print("datetime:", rtc.datetime())
        return send_file('html/success.html')
    return send_file('/html/time.html')


@app.route('/network', methods=['GET', 'POST'])
def network(request):
    if request.method == 'POST':
        ssid_1 = request.form.get('ssid1')
        pw_1 = request.form.get('password1')
        network_1 = {"ssid": ssid_1, "password": pw_1}
        change_stored_networks([network_1])
        return send_file('html/success_network.html')
    return send_file('/html/network.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings(request):
    if request.method == 'POST':
        rtc = RTC()
        timekeeper = Timekeeper()
        date = time = request.form.get('date').split('-')
        time = request.form.get('time').split(':')
        # [INFO]  Year | Month | Day | Weekday | Hour | Minute | Second | Microseconds
        rtc.datetime((date[0], date[1], date[2], 0, time[0], time[1], 0, 0))
        timekeeper.set_datetime((date[0], date[1], date[2], 0, time[0], time[1], 0, 0))
        print("Set datetime to: ", (date[0], date[1], date[2], 0, time[0], time[1], 0, 0))
        return send_file('html/success_time.html')
    return send_file('/html/settings.html')


@app.get('/success_network')
def success_network(request):
    return send_file('/html/success_network.html')


@app.get('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


class WebServer:
    def __init__(self, logger):
        self.log = logger
        # self.memory = memory
        
    def start(self):
        # self.memory.clean_ram()
        self.log.info('Start Webserver')
        try:
            app.run(port=80, debug=True)
        except OSError as e:
            self.log.warning(e)
        # self.memory.clean_ram()
        self.log.info('Shutdown Webserver')