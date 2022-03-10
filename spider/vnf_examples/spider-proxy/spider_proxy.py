from flask import Flask
from vnf_interface import VNF

class SpiderProxy(VNF):
    def _process_data(self, request):
        return request.json


if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = SpiderProxy(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
