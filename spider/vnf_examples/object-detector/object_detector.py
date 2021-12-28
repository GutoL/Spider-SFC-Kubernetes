from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from imageai.Detection import ObjectDetection
import os
from vnf_interface import VNF

# https://towardsdatascience.com/object-detection-with-10-lines-of-code-d6cb4d86f606
def object_detection(image):
    
    execution_path = os.getcwd()

    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath(os.path.join(execution_path , "resnet50_coco_best_v2.1.0.h5"))
    detector.loadModel()

    # input_image = os.path.join(execution_path , "image.jpg")
    detections = detector.detectObjectsFromImage(input_image=image, 
                                                output_image_path=os.path.join(app.config['UPLOAD_FOLDER'] , 
                                                "imagenew.jpg"))

    result = {}
    for eachObject in detections:
        # print(eachObject["name"] , " : " , eachObject["percentage_probability"])
        result[eachObject["name"]] = eachObject["percentage_probability"]
    
    return result

class ObjectDetector(VNF):
    def _process_data(self, request):
        UPLOAD_FOLDER = 'uploads'

        file = Image.open(request.files['file'])

        extension = os.path.splitext(file.filename)[1]
        f_name = os.path.join(UPLOAD_FOLDER, 'image'+ extension)
        file.save(f_name)      

        result = object_detection(f_name)

        # response = jsonify('ok')
        return result


if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = ObjectDetector(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)

