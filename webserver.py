from machine import RTC

from microdot import Microdot
from microdot import send_file


app = Microdot()


@app.route('/html/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('html/' + path)


@app.route('/', methods=['GET', 'POST'])
def index(request):
    if request.method == 'POST':
        print("This is a post test")
        ssid1 = request.form.get('ssid1')
        print("ssid1:", ssid1)
        pw1 = request.form.get('password1')
        print("pw1:", pw1)
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