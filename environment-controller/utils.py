import json

class Utils:

    @staticmethod
    def create_deployment_json(vnf_name, node_name, resources):
        
        deployment_json_format = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata":{
                "name": vnf_name,
                "labels":{
                    "app":vnf_name
                }
            },
            "spec": {
                "replicas" : 1,
                "selector": {
                    "matchLabels" : {
                        "app":vnf_name
                    }
                },
                "template" : {
                "metadata" : {
                    "labels" : {
                        "app":vnf_name
                    }
                },
                "spec":{
                    "containers":[
                        {
                            "name":vnf_name,
                            "image":vnf_name+":latest",
                            "ports":[
                            {
                                "containerPort": 5000 
                            }
                            ],
                            "imagePullPolicy": "Never",
                            "limits":resources
                        }
                    ]
                }
            }
            }
        }

        return json.dumps(deployment_json_format, indent=4)
    
    @staticmethod
    def create_service_json_format(service_name, vnf_name):
        
        service_json_format = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata":{
                "name": service_name
            },
            "spec":{
                "selector":{
                    "app": vnf_name
                },
                "ports":[{"protocol": "TCP","port": 5000,"targetPort": 5000}],
                "type": "LoadBalancer"
            }

        }

        return json.dumps(service_json_format, indent=4)
