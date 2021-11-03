#app.py
from flask import Flask, json, request, jsonify

import numpy as np
import cv2
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
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

 
@app.route('/')
def main():
    return 'Homepage'
 

# curl -F "file=@image.png" http://127.0.0.1:5000/compress
@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        
        img = Image.open(request.files['file'])
        img = np.array(img)
        img = cv2.resize(img,(224,224))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)

        # cv2.imshow('image',img)
        # cv2.waitKey(0)
        #model.predict(img)

        dumped = json.dumps(img, cls=NumpyEncoder)

        fact_resp = {'image':dumped} 
        return jsonify(fact_resp)

        # file = request.files['image']
        # print(file.read())
        
        # extension = os.path.splitext(file.filename)[1]
        # f_name = 'foto'+ extension #str(uuid.uuid4()) + extension
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        # return json.dumps({'filename':f_name})

if __name__ == '__main__':
    app.run(debug=True)
