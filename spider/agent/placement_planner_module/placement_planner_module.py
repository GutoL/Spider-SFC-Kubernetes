from flask_classful import FlaskView, route, request
from flask import Flask
import numpy as np
import sys
from bson import json_util
import json
from random import randint


class PlacementPlannerModule(FlaskView):
    route_base = '/'

    @route('/define_placement/', methods=['POST'])
    def define_placement(self)-> str:

        obs = json.dumps(request.json, indent=4, default=json_util.default)

        # number_of_candidate_nodes = int((len(obs)-4)/4)-1
        # candidate = random.randint(0,number_of_candidate_nodes)        
        candidate = 0
        redundancy = randint(0,1)

        return {'candidate':candidate, 'redundancy':redundancy}

if __name__ == '__main__':
    app = Flask(__name__)
    PlacementPlannerModule.register(app)
        
    app.run(host="0.0.0.0", port=2500, debug=True)
