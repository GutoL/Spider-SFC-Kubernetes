import psutil
from threading import Thread
import time

from flask import Flask
from flask_classful import FlaskView

class NetworkMonitor(Thread):
    def __init__ (self, interface):
        self.interface = interface
        self.time_window = 2 # seconds
        Thread.__init__(self)

    def _get_bytes_received(self):
        # bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout
        return list(psutil.net_io_counters(pernic=True)[self.interface])[1]
    def _get_bytes_sent(self):
        return list(psutil.net_io_counters(pernic=True)[self.interface])[0]

    def get_consumption(self):
        
        received_bytes = self._get_bytes_received()
        sent_bytes = self._get_bytes_sent()
        time.sleep(self.time_window)

        received_bytes = self._get_bytes_received() - received_bytes
        sent_bytes = self._get_bytes_sent() - sent_bytes

        return {'received_bytes':received_bytes,'sent_bytes':sent_bytes,'total':received_bytes+sent_bytes}




class Monitor(FlaskView):
    route_base = '/'

    def __init__(self) -> None:
        self.network_monitor = NetworkMonitor('wlo1')
        self.network_monitor.start()        

    def index(self):
        return str(self.network_monitor.get_consumption())


if __name__ == '__main__':
    app = Flask(__name__)
    Monitor.register(app)
        
    app.run(host='0.0.0.0', port=5000)
