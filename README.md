# k8s-SFC

To setup the environment with four nodes:

master node (master node of k8s)
minion-1 (first node to deploy the VNFs in the k8s)
minion-2 (second node to deploy the VNFs in the k8s)
main node

*** Install the docker and kuberbetes in the master, minion-1, and minion-2 nodes. Remember of disable the swap, run the API proxy of master (run: kubectl proxy --port=8080 &), and enable the docker api.

*** Remember that you need to add labels to the nodes where the VNFs will be placed. These labels are used by the k8s to define in which node each VNF will be placed. To define the label of minion-1, for instance, use: kubectl label nodes minion-1 nodetype=minion-1

*** In the minion nodes, you need to copy the folder monitor/daemon. Then run the setup.sh script in order to install all dependencies. Then, update the file node_config.json in order to specify all node information (for instance the informations about id and links).

*** In the basic setup, the environment controller runs in the same node of master k8s. Therefore, copy the folder environment-controller to the master node and install all python requirements from requirements.txt file. Then, you must to modify the system.config file to add the system configuration information. Basically, you should provide the the basic k8s url, the k8s urls for deployments and services, and the dockerfile name.


*** In the main node, you can run the monitor handler. Firstly, you need to install the mongo db in the main machine, since the information collected you be saved as a graph. Then, install the requirements from the requirements.txt file. You also must to edit the file config.json, to add the information about all nodes from infrastructure (ip and name of nodes) Then, run the file monitor.py, which is an API that will call the daemon of all nodes in the infrastructure and collect the data about the nodes and links. To call this API, run the script collector.py, that will gather all information about the nodes and links and save it in the mongo db.
