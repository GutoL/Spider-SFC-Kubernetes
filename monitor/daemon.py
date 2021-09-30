import psutil
from flask import Flask
from flask_classful import FlaskView
import sys

class MonitorDaemon(FlaskView):

    route_base = '/'

    def _get_cpu_consumption(self):
        return psutil.cpu_percent()
    
    def _get_memory_consumption(self):
        return psutil.virtual_memory().percent
    
    def _get_storage_consumption(self, path='/'):
        return psutil.disk_usage(path).percent

    def index(self):
        json = {
            'cpu':self._get_cpu_consumption(),
            'memory':self._get_memory_consumption(),
            'storage': self._get_storage_consumption()
        }
        return json



if __name__ == '__main__':
    app = Flask(__name__)
    MonitorDaemon.register(app)

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 4000
        
    app.run(host='0.0.0.0', port=port)
