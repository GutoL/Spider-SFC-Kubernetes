from flask import Flask, json
from vnf_interface import VNF

import numpy as np
from PIL import Image

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Destination(VNF):
    def _process_data(self, request):
        
        img = Image.open(request.files['file'])
        img = np.array(img)

        dumped = json.dumps(img, cls=NumpyEncoder)

        fact_resp = {'data': dumped, 'shape': img.shape}
        
        return fact_resp


if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = Destination(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
