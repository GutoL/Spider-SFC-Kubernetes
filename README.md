# Spider: Kubernetes-based Service Function Chaining (SFC) Framework
Spider is a framework designed to facilitate the creation and management of Service Function Chains (SFCs) using Kubernetes as the underlying orchestration platform. The framework comprises three main components:

- Spider Core: The core of the framework, responsible for orchestrating the deployment and management of SFCs within a Kubernetes environment as containers.

- API: An interface that enables users to interact with the core functions of the Spider framework, allowing for seamless integration and control over SFC configurations.

- Repositories: These modules implement functions to access and manage data within a MongoDB database, providing robust storage and retrieval capabilities for SFC configurations and operational data.

By leveraging Kubernetes and MongoDB, Spider offers a resilient and scalable infrastructure for orchestrating SFCs, enabling users to build and manage distributed network services with ease. Whether deploying microservices, managing network traffic, or optimizing resource allocation, Spider empowers users to achieve efficient and reliable service delivery in modern cloud environments.

This guide provides instructions for setting up a Service Function Chaining (SFC) environment using Spider. The environment consists of four nodes:

- **master node**: The primary node managing Kubernetes.
- **minion-1**: The first node for deploying Virtual Network Functions (VNFs) in Kubernetes.
- **minion-2**: The second node for deploying VNFs in Kubernetes.
- **main node**: The main node in the infrastructure.

## Setup Instructions

### Prerequisites

- Install Docker and Kubernetes on the master, minion-1, and minion-2 nodes. Disable swap, run the Kubernetes API proxy on the master node (`kubectl proxy --port=8080 &`), and enable the Docker API.
- Provide access to the VNFs to access the Kubernetes API by applying the `pod_authorization.yaml` file located in the `utils` folder. Run the following commands in the master node:
  ```bash
  kubectl create -f pod_authorization.yaml
  systemctl restart kubelet.service
  ```

### Node configuration
Add labels to the nodes. These labels are used by the Kubernetes to define in which node each VNF will be placed. Use the following command to define labels, for example, for minion-1:
```bash
kubectl label nodes minion-1 nodetype=minion-1
```

### Configuration Steps
1. Minion Nodes:
  - Copy the monitor/daemon folder and run the setup.sh script to install dependencies. Update node_config.json to specify node information (for instance the informations about id and links).
2. Master Node:
  - In the basic setup, the environment controller runs in the same node of Kubernetes master. Copy the environment-controller folder to the master node. Install Python requirements from requirements.txt. Modify system.config to add system configuration information. Basically, you must provide the the basic Kubernetes url, the Kubernetes urls for deployments and services, and the dockerfile name. Run main.py in the environment-controller folder.
3. Main Node:
  - In the main node, you can run the monitor handler. Install MongoDB, since the information collected you be saved as a graph. Edit config.json to add information about all infrastructure nodes (ip and name of nodes). Run the file monitor.py, which is an API that will call the daemon of all nodes in the infrastructure and collect the data about the nodes and links. Finally, run the script collector.py, that will gather all information about the nodes and links and save it in the MongoDB.

### Starting the scenario
- Master node:
```bash
sudo swapoff -a
kubectl proxy --port=8080 &
python3 environment-controller/main.py start
python3 daemon/daemon.py
```

- Minion Node:
  ```bash
  sudo swapoff -a
  python3 daemon/daemon.py
  ```
  
- Main Node:
  - Check MongoDB status:
  ```bash
    systemctl status mongod.service
  ```
  - If MongoDB is not running, start it:
  ```bash
  chmod +x environment-controller/start_mongo.sh
  sudo ./environment-controller/start_mongo.sh
  ```
- Start the monitor, collector, agent, and orchestrator:
```bash
  monitor/monitor-handler/monitor.py start
  python monitor/monitor-handler/collector.py start
  python agent/agent.py start
  python orchestrator/orchestrator.py
```
- To call the orchestrator:
```bash
  curl -X POST -H "Content-Type: application/json" -d @orchestrator/sfc-request-image.json http://192.168.0.209:4996/sfc
```
