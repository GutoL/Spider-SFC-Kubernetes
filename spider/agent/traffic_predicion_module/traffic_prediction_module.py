from flask_classful import FlaskView, route, request
from flask import Flask
import numpy as np
import sys

sys.path.insert(1, '../../../repository/')
from sfc_traffic_repository import SfcTrafficRepository


class TrafficPredictionModule(FlaskView):
    route_base = '/'

    def __init__(self) -> None:
        self.sfc_traffic_repository = SfcTrafficRepository()

    def _call_prediction_model(self, data):
        return np.mean(data)

    @route('/predict/<sfc_id>', methods=['GET'])
    def predict(self, sfc_id)-> str:

        sfc_traffic_info = self.sfc_traffic_repository.get_sfc_traffic_by_sfc_id(sfc_id)[0]

        # print(sfc_traffic_info)

        if len(sfc_traffic_info)>0:
            sfc_traffic = [x['traffic'] for x in sfc_traffic_info['traffic']]
            prediction = self._call_prediction_model(sfc_traffic)
        
        return {'prediction':prediction, 'physical_links': sfc_traffic_info['physical_links']}

if __name__ == '__main__':
    app = Flask(__name__)
    TrafficPredictionModule.register(app)
        
    app.run(host="0.0.0.0", port=2501, debug=True)
