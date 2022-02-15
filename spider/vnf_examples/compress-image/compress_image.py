from flask import Flask, json, jsonify

import numpy as np
import cv2
from PIL import Image

from datetime import datetime

from vnf_interface import VNF

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


class ImageCompressor(VNF):
    def _process_data(self, request):
        img = Image.open(request.files['file'])
        img = np.array(img)
        img = cv2.resize(img,(224,224))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)

        # cv2.imshow('image',img)
        # cv2.waitKey(0)
        #model.predict(img)

        dumped = json.dumps(img, cls=NumpyEncoder)

        fact_resp = {'data': dumped, 'shape': img.shape}
        
        return fact_resp

if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = ImageCompressor(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
