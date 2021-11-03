from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from imageai.Detection import ObjectDetection
import os

app = Flask(__name__)
 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    for eachObject in detections:
        print(eachObject["name"] , " : " , eachObject["percentage_probability"] )
 
@app.route('/')
def main():
    return 'Homepage'
 

# curl -F "file=@image.png" http://127.0.0.1:5000/compress
@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        
        file = request.files['file']
        
        extension = os.path.splitext(file.filename)[1]
        f_name = os.path.join(app.config['UPLOAD_FOLDER'], 'image'+ extension)
        file.save(f_name)      

        object_detection(f_name)

        response = jsonify('ok')
        return response


if __name__ == '__main__':
    app.run(debug=True,port=4500)
