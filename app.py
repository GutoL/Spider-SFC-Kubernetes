from kubernetes import client, config
from flask import Flask
import requests
import json

app = Flask(__name__)

def get_data(vnf_config):
    data = ''
    next_vnf = vnf_config['next_vnf']
    last_vnf = vnf_config['last_vnf']

    try:
       url = 'http://'+next_vnf+':5000/'
       print(url)
       r = requests.get(url = url)
       data = json.dumps(r.json())

    except:
       if last_vnf:
          data = 'OK'
       else:
          data = 'error'

    return {'response':data}


@app.route('/')
def index():
    f = open("config_vnf.json")
    vnf_config = json.load(f)

    return get_data(vnf_config)
    #return 'Hello, Docker!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
