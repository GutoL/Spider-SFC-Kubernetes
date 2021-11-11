from flask import Flask
from flask_classful import FlaskView, route, request

class Orchestrator(FlaskView):
    route_base = '/'

    @route('/sfc', methods=['POST'])
    def create_sfc(self)-> str:
        request_json = request.json

        # 1 - get status of infrastructure from collector.py
        # 2 - call the agent to create the SFC request
        # 3 - send the SFC request to the environment controller (main.py)

        return ''


app = Flask(__name__)
Orchestrator.register(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
