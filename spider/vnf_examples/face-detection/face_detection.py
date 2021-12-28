from flask import Flask #, json, jsonify
import json
import re
import numpy as np
import cv2
from PIL import Image

from vnf_interface import VNF

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class FaceDetection(VNF):
    def _process_data(self, request):
        # https://towardsdatascience.com/face-detection-in-2-minutes-using-opencv-python-90f89d7c0f81

        img = np.asarray(re.findall(r'\d+', request.json['data']), dtype=np.uint8) # converting the array in string format to array of numbers

        img = np.reshape(img, request.json['shape']) # reshaping the image

        # Load the cascade
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Convert into grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # Encoding the result to send back
        result = json.dumps({x: face for x, face in enumerate(faces)}, cls=NumpyEncoder)
        
        return result

if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = FaceDetection(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
