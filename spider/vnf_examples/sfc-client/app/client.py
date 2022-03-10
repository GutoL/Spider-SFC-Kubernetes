# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask

from flask import Flask, render_template, request, redirect, url_for
import requests
from kubernetes import client, config

def get_vnf_service_ip(service_name):
    config.load_kube_config() # running outside pod
    #config.load_incluster_config() # running inside pod

    v1 = client.CoreV1Api()
    
    services = v1.list_service_for_all_namespaces(watch=False)
    for svc in services.items:
        if service_name == str(svc.metadata.name):
            return svc.spec.cluster_ip

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']

    files = {
        'file': ('image.jpg', uploaded_file),
    }

    if uploaded_file.filename != '':
        # uploaded_file.save(uploaded_file.filename)
        response = requests.post(url, files=files)
        print(response.content)

    return redirect(url_for('index'))

if __name__ == '__main__':
    first_vnf_service_name = 'my-sfc-source-service'
    vnf_port = 5000

    url = get_vnf_service_ip(first_vnf_service_name)
    url = 'http://'+str(url)+':'+str(vnf_port)

    app.run(host="0.0.0.0", port=4500, debug=True)
