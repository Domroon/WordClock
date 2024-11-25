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


@app.route('/set', methods=['GET', 'POST'])
def set_time(request):
    if request.method == 'POST':
        ssid = request.form.get('ssid1')
        pw = request.form.get('password1')
        f = open('stored_networks.txt', 'w')
        f.write(ssid)
        f.write("|")
        f.write(pw)
        f.close()
        return send_file('/html/success.html')
    return send_file('/html/index.html')


@app.route('/success', methods=['GET', 'POST'])
def success(request):
    return send_file('/html/success.html')


@app.get('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


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