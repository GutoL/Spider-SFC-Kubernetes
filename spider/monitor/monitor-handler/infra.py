import networkx as nx
import random
import copy
import geopy.distance
import networkx.algorithms.community as nxcom


class InfrastructureGraph(nx.MultiGraph):

  def __init__(self,graph_as=None,AS_number=50,latitude=19.99,longitude=73.78,
               lat_list=None, long_list=None,resources_ranges=None, 
               vnf_list=None, nodes_support_all_vnfs=False, add_fat_tree=False, 
               servers_number_micro=2, servers_number=4,
               add_clusters=False):
    
    self.graph_as = graph_as
    self.AS_number = AS_number
    self.latitude = latitude
    self.longitude = longitude
    self.lat_list = lat_list
    self.long_list = long_list
    self.resources_ranges = resources_ranges
    self.nodes_support_all_vnfs = nodes_support_all_vnfs
    self.add_fat_tree = add_fat_tree
    self.servers_number_micro = servers_number_micro
    self.servers_number = servers_number
    self.add_clusters = add_clusters

    self.vnf_list = vnf_list
    self.components = ['cpu','memory','storage']

    self.create_graph()

  # def get_prob_failure_node(self,node,time):
  #   return 1-self.get_reliability_node(node,time)

  # def get_reliability_node(self,node,time):
  #   return math.exp(-(1/self.nodes[node]['mttf'])*time)

  def create_graph(self):
    super(InfrastructureGraph, self).__init__()

    if self.graph_as == None:
      self.graph_as = nx.generators.internet_as_graphs.random_internet_as_graph(n=self.AS_number,seed=0)
    
      if self.lat_list is None or self.long_list == None:
        self.lat_list, self.long_list = self.generate_random_location(self.latitude,self.longitude,self.AS_number)

      attrs = {}
      for x,node in enumerate(self.graph_as.nodes):
        attrs[node] = {'latitude':self.lat_list[x],'longitude':self.long_list[x]}

      nx.set_node_attributes(self.graph_as, attrs)
    
    if self.add_fat_tree and self.as_graph == None:
      self.as_graph, self.number_of_dcs = self.generate_composed_graph(self.graph_as,self.servers_number_micro, self.servers_number)

      general_info_dcs = self.generate_dc_information(self.vnf_list,self.nodes_support_all_vnfs)

      self.as_graph = self.add_attributes_to_composed_graph(graph=self.as_graph,resources_ranges=self.resources_ranges,
                                                       general_info_dcs=general_info_dcs,
                                                       attr_nodes=None, attr_links=None)
    elif not self.add_fat_tree:
      self.as_graph = self.add_attributes_to_simple_graph(graph=self.graph_as,resources_ranges=self.resources_ranges,
                                                     vnf_list=self.vnf_list,
                                                     nodes_support_all_vnfs=self.nodes_support_all_vnfs,
                                                     lat_list=self.lat_list,long_list=self.long_list,
                                                     attr_nodes=None, attr_links=None)

    elif self.add_fat_tree and self.as_graph is not None:
      print('Error: you cannot add fat trees in an existing graph!')
      return None
                      
                                     
    self.add_nodes_from(self.as_graph.nodes(data=True))
    self.add_edges_from(self.as_graph.edges(data=True))

    if self.add_clusters:
      self.create_clusters()

  def print_nodes_status(self):
    for node in self.nodes:
      print(node,self.nodes[node]['available_resources'])
    print('----------')
  
  def print_edges_status(self):
    for edge in self.edges:
      print(edge, self.edges[edge]['available_resources'])
    print('----------')

  # This function generates random values about the nodes
  # Input: resources_ranges: a dict with the baseline values and the variabilityty
  # Returns: the random values for each feature of the node
  def generate_nodes_attr_variability(self,resources_ranges):

    if random.uniform(0, 1) > 0.5:
      factor = 1+random.uniform(0,resources_ranges['variability'])
    else:
      factor = 1-random.uniform(0,resources_ranges['variability'])
    
    cpu = int(resources_ranges['cpu']*factor)
    memory = int(resources_ranges['memory']*factor)
    storage = int(resources_ranges['storage']*factor)
    cost = int(resources_ranges['node_cost']*factor)
    energy = int(resources_ranges['energy']*factor)
    
    mttr = resources_ranges['mttr_node']*factor
    mttf = resources_ranges['mttf_node']*factor
    
    if cost <= 0:
      cost = 1
    
    F = (math.log(cost)-math.log(mttf))/mttf
    # print("F",F)
    # if F > 0:
    cost = mttf*math.exp(F*mttf) 

    return cpu,memory,storage,cost,mttf,mttr,energy
  
  def generate_nodes_attr(self,resources_ranges):

    cpu = int(resources_ranges['cpu'])
    memory = int(resources_ranges['memory'])
    storage = int(resources_ranges['storage'])
    cost = int(resources_ranges['node_cost'])
    energy = int(resources_ranges['energy'])
    
    mttr = resources_ranges['mttr_node']
    mttf = resources_ranges['mttf_node']

    return cpu,memory,storage,cost,mttf,mttr,energy
  
  # This function add capacity attributes to the nodes (cpu, memory, storage, and cost) and edges (delay, bandwidth, and cost) of the graph
  # Input: graph: the graph to be updated,
  #        resources_ranges: a dict that describes the range of resources for the nodes and edges,
  #        general_info_dcs: a dict that describes the information about the DC. For now, this information is only the suppported VNFs by the DCs
  #        attr_nodes and attr_links: the attributes of nodes and links, respectiely. If these parameters are None, they are generated based on the other parameters of this function
  # Returns: the graph with the attributes generated
  def add_attributes_to_composed_graph(self, graph, resources_ranges, general_info_dcs,
                                       attr_nodes=None, attr_links=None):
    
    # GENERATING NODES
    if attr_nodes == None:
      
      attr_nodes = {}
      
      # for node in range(graph.number_of_nodes()):
      for node in graph.nodes:
        
        cpu,memory,storage,cost,mttf,mttr,energy = self.generate_nodes_attr(resources_ranges)

        attr_node = { 
          'status': 'operational', 
          # 'type': 'server', 
          'resources': {'cpu': cpu,
                        'memory': memory,
                        'storage': storage,
                        },
          'node_cost': cost,
          'mttf':mttf,
          'mttr':mttr,
          'availability':mttf/(mttf+mttr),
          'energy':energy,
          'metadata': [{'metadata_key': 'lat', 'value':graph.nodes[node]['latitude']},
                      {'metadata_key': 'long', 'value':graph.nodes[node]['longitude']}], 
          'capabilities': {}
        }

        attr_node['available_resources'] = copy.deepcopy(attr_node['resources'])

        if 'dc_id' in graph.nodes[node]:
          attr_node['capabilities'] = {'supported_VNFs':general_info_dcs[graph.nodes[node]['dc_id']]['supported_vnfs']}                              


        attr_node['id'] = str(node)
        attr_node['original_id'] = str(node)
        attr_node['name'] = 'node_name_'+str(node)
        
        attr_node['ports'] = [] # the ports will be added following the graph edges
        attr_node['placed'] = {} # this dict will be populated when the sfcs are added to the nodes
        
        attr_nodes[node] = copy.deepcopy(attr_node)

    nx.set_node_attributes(graph,attr_nodes)

    # GENERATING LINKS
    if attr_links == None:
      attr_links = {}
      i=0
      for edge in graph.edges:

        coords_1 = (graph.nodes[edge[0]]['latitude'],graph.nodes[edge[0]]['longitude'])
        coords_2 = (graph.nodes[edge[1]]['latitude'],graph.nodes[edge[1]]['longitude'])
        
        distance = geopy.distance.vincenty(coords_1, coords_2).km # geopy==1.17.0
        # distance = geopy.distance.geodesic(coords_1, coords_2).km # geopy==2.1.0

        # Generating the ports for this edge, based on the nodes ids
        port_node_1 = 's'+str(edge[0])+'p'+str(len(graph.nodes[edge[0]]['ports']))
        port_node_2 = 's'+str(edge[1])+'p'+str(len(graph.nodes[edge[1]]['ports']))
        
        graph.nodes[edge[0]]['ports'].append(port_node_1)
        graph.nodes[edge[1]]['ports'].append(port_node_2)

        bandwidth = 10 #random.randrange(resources_ranges['bandwidth'][0],resources_ranges['bandwidth'][1]),
        cost_link = random.randrange(resources_ranges['cost_edge'][0],resources_ranges['cost_edge'][1])

        attr_edge = {'id': i,
        'src_port': port_node_1, 'dst_port': port_node_2, 
        'src_node': edge[0], 'dst_node': edge[1],
        'resources': {'delay': distance,
                      'bandwidth': bandwidth,
                      'cost_link': cost_link},
        }
        
        attr_edge['available_resources'] = copy.deepcopy(attr_edge['resources'])

        attr_links[edge] = copy.deepcopy(attr_edge)
        i+=1

    nx.set_edge_attributes(graph,attr_links)

    return graph

  def add_attributes_to_simple_graph(self, graph, resources_ranges, vnf_list,nodes_support_all_vnfs=False,
                                     lat_list=None, long_list=None, attr_nodes=None, attr_links=None):
    # GENERATING NODES
    if attr_nodes == None:
      
      attr_nodes = {}
      
      for i,node in enumerate(graph.nodes):
        
        vnfs_number = random.randrange(1,len(vnf_list)) # number of VNFs that the node can receive
        
        cpu,memory,storage,cost,mttf,mttr,energy = self.generate_nodes_attr(resources_ranges)
        
        attr_node = { 
          'status': 'operational', 
          # 'type': 'server', 
          'resources': {'cpu': cpu,
                        'memory': memory,
                        'storage': storage,
                        },
          'node_cost': cost,
          'mttf':mttf,
          'mttr':mttr,
          'availability':mttf/(mttf+mttr),
          'energy':energy,
          # 'metadata': [{'metadata_key': 'lat', 'value':lat_list[i]},
          #             {'metadata_key': 'long', 'value':long_list[i]}], 
          # 'capabilities': {'supported_VNFs':random.sample(vnf_list,k=vnfs_number)}          
        }

        if 'latitude' in graph.nodes[node]:
          attr_node['metadata'] = [{'metadata_key': 'lat', 'value':graph.nodes[node]['latitude']},
                      {'metadata_key': 'long', 'value':graph.nodes[node]['longitude']}],
        else:
          attr_node['metadata'] = [{'metadata_key': 'lat', 'value':lat_list[i]},
                      {'metadata_key': 'long', 'value':long_list[i]}]
          attr_node['latitude'] = lat_list[i]
          attr_node['longitude'] = long_list[i]

        if nodes_support_all_vnfs:
          attr_node['capabilities'] = {'supported_VNFs':vnf_list}
        else:
          attr_node['capabilities'] = {'supported_VNFs':random.sample(vnf_list,k=vnfs_number)}
        
        attr_node['available_resources'] = copy.deepcopy(attr_node['resources'])

        attr_node['id'] = str(node)
        attr_node['original_id'] = str(node)
        attr_node['name'] = 'node_name_'+str(node)
        
        attr_node['ports'] = [] # the ports will be added following the graph edges
        attr_node['placed'] = {} # this dict will be populated when the sfcs are added to the nodes
        
        attr_nodes[node] = copy.deepcopy(attr_node)

    nx.set_node_attributes(graph,attr_nodes)

    # GENERATING LINKS
    if attr_links == None:
      attr_links = {}
      i=0
      for edge in graph.edges:

        coords_1 = (graph.nodes[edge[0]]['latitude'],graph.nodes[edge[0]]['longitude'])
        coords_2 = (graph.nodes[edge[1]]['latitude'],graph.nodes[edge[1]]['longitude'])
        # distance = geopy.distance.vincenty(coords_1, coords_2).km
        distance = geopy.distance.geodesic(coords_1, coords_2).km

        port_node_1 = 's'+str(edge[0])+'p'+str(len(graph.nodes[edge[0]]['ports']))
        port_node_2 = 's'+str(edge[1])+'p'+str(len(graph.nodes[edge[1]]['ports']))
        
        graph.nodes[edge[0]]['ports'].append(port_node_1)
        graph.nodes[edge[1]]['ports'].append(port_node_2)

        bandwidth = resources_ranges['bandwidth']
        cost_link = resources_ranges['cost_edge']

        attr_edge = {'id': i,
        'src_port': port_node_1, 'dst_port': port_node_2, 
        'src_node': edge[0], 'dst_node': edge[1],
        
        'resources': {'delay': distance,
                      'bandwidth': bandwidth,
                      'cost_link': cost_link},
        }

        attr_edge['available_resources'] = copy.deepcopy(attr_edge['resources'])
        
        attr_links[edge] = copy.deepcopy(attr_edge)
        i+=1

    nx.set_edge_attributes(graph,attr_links)

    return graph

  # This function changes the node id label, adding a prefix
  # Input: graph: the graph to be modified
  #        prefix: the prefix that will be added in the node ids
  # Returns: the graph modified
  def change_label_graph(self,graph,prefix=''):
    temp_graph = nx.Graph()

    mapping = {}
    for node in graph.nodes:
      mapping[node] = prefix + str(node)
      
    return nx.relabel_nodes(graph, mapping)

  # This function connects the DC gragh to the AS graph. We connect the first tree nodes of DC graph (normally are switchs nodes) to the AS node. However other strategies can be used
  # Input: as_graph: the AS graph to be connected to the DC graph
  #        as_node: the id of node in the AS graph that the DC graph will be connected
  #        dc_graph: the DC graph to be connected to the AS graph
  # Returns: the AS graph with the edges created
  def connect_as_to_dc(self,as_graph,as_node,dc_graph):
    as_graph.add_edge(as_node, list(dc_graph.nodes)[0]) # connecting the AS graph with the first node of DC graph
    as_graph.add_edge(as_node, list(dc_graph.nodes)[1]) # connecting the AS graph with the second node of DC graph
    as_graph.add_edge(as_node, list(dc_graph.nodes)[2]) # connecting the AS graph with the third node of DC graph

    return as_graph

  # This function generates the DC graph using the fat-tree infrastructure and add it in the AS graph
  # Input: as_graph: the AS graph where the DC graphs will be connected
  #        as_node: The node from AS graph where the fat-tree
  #        servers_number: number of servers in the DC graph
  #        dc_id: the id of node in the AS graph. This node id is stored as a DC id in the nodes of DC graph
  #        latitude and longitude: location of AS node. We assume that the location of the AS node is the same of nodes of DC graph
  # Returns: the DC graph generated using the fat-tree topology
  def create_dc_graph(self,as_graph,as_node, servers_number,dc_id,latitude,longitude):
    k = round((4*servers_number)**(1/3))
    if k % 2 == 1:
      k += 1

    dc_graph = fnss.fat_tree_topology(k=k)
    # dc_graph = fnss.bcube_topology(n=5, k=1)
    
    dc_graph = self.change_label_graph(dc_graph,str(as_node)+'_')

    # attr = {'dc_id':dc_id,
    #         'latitude': latitude,
    #         'longitude':longitude}

    # nx.set_node_attributes(dc_graph, attr)

    nx.set_node_attributes(dc_graph, dc_id, 'dc_id')
    nx.set_node_attributes(dc_graph, latitude, 'latitude')
    nx.set_node_attributes(dc_graph, longitude, 'longitude')
    
    as_graph.add_nodes_from(dc_graph.nodes(data=True))
    as_graph.add_edges_from(dc_graph.edges(data=True))
    
    as_graph = self.connect_as_to_dc(as_graph,as_node,dc_graph)

    return as_graph

  # This function generates the Fat tree graphs and connects them to the AS graph
  # Input: graph_as: the AS graph where the fat-tree graphs will be connected
  #       servers_number_micro: number of servers in the fat-tree graph that will be connected in nodes of type M
  #       server_number: number of servers in the fat-tree graph that will be connected in nodes of type CP
  # Returns: the the AS graph combined with the fat-tree graph
  def generate_composed_graph(self,graph_as,servers_number_micro=2,server_number=2):
    as_graph = nx.Graph()
    as_graph.add_nodes_from(graph_as.nodes(data=True))
    as_graph.add_edges_from(graph_as.edges(data=True))

    number_of_dcs = 0

    attr_nodes = {}
    for i, node in enumerate(graph_as.nodes):
      
      if as_graph.nodes[node]['type'] == 'M': # micro DC
        as_graph = self.create_dc_graph(as_graph=as_graph,as_node=i,servers_number=servers_number_micro,
                                  dc_id=number_of_dcs,
                                  latitude=as_graph.nodes[node]['latitude'],
                                  longitude=as_graph.nodes[node]['longitude'])
        number_of_dcs += 1
        
      elif as_graph.nodes[node]['type'] == 'CP': # DC
        as_graph = self.create_dc_graph(as_graph=as_graph,as_node=i,servers_number=server_number,
                                  dc_id=number_of_dcs,
                                  latitude=as_graph.nodes[node]['latitude'],
                                  longitude=as_graph.nodes[node]['longitude'])
        number_of_dcs += 1
    
    
    return as_graph, number_of_dcs


  # This function generates a random list of lat/long locations near to the lat/long passed as parameter
  # Input: lat: latitude value
  #        long: longitude value
  #        num_points: number of points to be generated
  # Returns: two lists with the lat long values each one
  def generate_random_location(self,lat, lon, num_points=1):
    
    if num_points == 1:
      return lat+random.random()/100, lon+random.random()/100
    
    else:

      lat_list = []
      long_list = []

      for _ in range(num_points):
        lat_list.append(lat+random.random()/100)
        long_list.append(lon+random.random()/100)

      return lat_list, long_list

  # This function generate a list of random VNFs for each DC
  # input: number_of_dcs: number of DCs present in the graph
  #      vnf_list: all VNFs to be considered in the infrastrucuture
  # returns: general_info_dcs: a dict with the suppported VNFs for each DC
  def generate_dc_information(self,vnf_list,nodes_support_all_vnfs=False):
    general_info_dcs = {}

    for x in range(self.number_of_dcs):
      if nodes_support_all_vnfs:
        general_info_dcs[x] = {'supported_vnfs':vnf_list}
      else:  
        general_info_dcs[x] = {'supported_vnfs':random.sample(vnf_list,random.randint(1,len(vnf_list)))} # getting random VNFs that this DC will support
        
    return general_info_dcs

  def get_nodes_by_resources(self, resources):
    nodes_ids = []
    
    for n in self.nodes:
      if ((self.nodes[n]['status'] == 'operational') and 
          (self.nodes[n]['resources']['cpu'] >= resources['cpu']) and
          (self.nodes[n]['resources']['memory'] >= resources['memory']) and
          (self.nodes[n]['resources']['storage'] >= resources['storage'])):
        nodes_ids.append(n)
    
    return nodes_ids

  def create_clusters(self):
    clusters = list(nxcom.greedy_modularity_communities(self))
    
    self.clusters = {}

    for cluster_id, nodes in enumerate(clusters):
      self.clusters[cluster_id] = list(nodes)

      for node in nodes:
        # Add 1 to save 0 for external edges
        self.nodes[node]['cluster'] = cluster_id #+ 1

  def get_node_consumption(self, node):
    ratio = {}
    for component in self.components:
      ratio[component] = self.nodes[node]['available_resources'][component]/self.nodes[node]['resources'][component]
    return ratio

  def get_nodes_consumption(self, aggregated=True, nodes=None):
    consumption_per_node = {}
    
    if nodes == None:
      nodes = self.nodes

    for node in nodes:
      if node in self.nodes:
        consumption_per_node[node] = self.get_node_consumption(node)
      else:
        consumption_per_node[node] = {component:0 for component in self.components}

    if not aggregated:
      return consumption_per_node
    
    components_weights = [1]*len(self.components)

    aggregated_consumption_per_node = {}

    for node in consumption_per_node:
      weighted_average = 0
      for i, component in enumerate(consumption_per_node[node]):
        weighted_average += (consumption_per_node[node][component] * components_weights[i])
      aggregated_consumption_per_node[node] = weighted_average/sum(components_weights)
    
    return aggregated_consumption_per_node
        

  def get_clusters_consumption(self, aggregated=True):
    consumption_per_cluster = {}

    for cluster in self.clusters:
      consumption = self.get_nodes_consumption(aggregated=aggregated, nodes=self.clusters[cluster])
      
      if aggregated:
        # calculating the average of the weighted average resources consumption
        consumption_per_cluster[cluster] = np.mean(list(consumption.values()))
      
      else:
        avg_consumption = {comp:0 for comp in self.components}
        for node in consumption:
          for comp in consumption[node]:
            avg_consumption[comp] += consumption[node][comp]

        avg_consumption = {comp:avg_consumption[comp]/len(consumption) for comp in avg_consumption}
        consumption_per_cluster[cluster] = avg_consumption
        
    return consumption_per_cluster
