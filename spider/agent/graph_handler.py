# plot networkx tutorial: https://towardsdatascience.com/customizing-networkx-graphs-f80b4e69bedf
import copy
import random
import networkx as nx
import matplotlib.pyplot as plt


class InfrastructureGraphHandler():

  def __init__(self, graph, block=4):
    self.graph = graph
    self.original_graph = copy.deepcopy(graph)
    self.redundancy_map = {}
    # self.sfcs = {}

    self.nodes_components = ['cpu','memory','storage']
    self.edges_components = ['bandwidth']

    # self.create_redundancy_map(block)

  def reset_infrastructure(self):
    self.graph = copy.deepcopy(self.original_graph)

  def update_infrastructure_after_vnf(self, sfc_instance_id, vnf_id, vnf_resources, flow_entry_resources,
                                      physical_node, physical_links, redundant):
    
    if sfc_instance_id not in self.graph.nodes[physical_node]['placed']:
      self.graph.nodes[physical_node]['placed'][sfc_instance_id] = [vnf_id]
      
    else:
      self.graph.nodes[physical_node]['placed'][sfc_instance_id].append(vnf_id)

    if vnf_id != 'source' and vnf_id != 'destination':
      for item in self.nodes_components:
        self.graph.nodes[physical_node]['available_resources'][item] -= vnf_resources[item]
    
    if not redundant:
      for s,d in physical_links:
        for item in self.edges_components:
          self.graph.edges[(s,d,0)]['available_resources'][item] -= flow_entry_resources[item]


  def update_infrastructure_after_sfc(self, sfc, sfc_instance_id, vnfs_placement, flow_entries_placement):
    
    for vnf_id in vnfs_placement:

      if sfc_instance_id not in self.graph.nodes[vnfs_placement[vnf_id]]['placed']:
        self.graph.nodes[vnfs_placement[vnf_id]]['placed'][sfc_instance_id] = [vnf_id]
      
      else:
        self.graph.nodes[vnfs_placement[vnf_id]]['placed'][sfc_instance_id].append(vnf_id)
      
      if sfc.nodes[vnf_id]['type'] != 'vnf': # because the source and destinations don't consume resources
        continue
      
      self.graph.nodes[vnfs_placement[vnf_id]]['available_resources']['cpu'] -= sfc.nodes[vnf_id]['resources']['cpu']
      self.graph.nodes[vnfs_placement[vnf_id]]['available_resources']['memory'] -= sfc.nodes[vnf_id]['resources']['memory']
      self.graph.nodes[vnfs_placement[vnf_id]]['available_resources']['storage'] -= sfc.nodes[vnf_id]['resources']['storage']

    for flow_entry in flow_entries_placement:
      for s,d in flow_entries_placement[flow_entry]:
        self.graph.edges[(s,d,0)]['available_resources']['bandwidth'] -= sfc.edges[flow_entry]['resources']['bandwidth']
  
  def add_sfc(self, sfc, sfc_instance_id, toy_placement=True, placed=True):

    if toy_placement:
      placed = False
      sfc, vnfs_placement, flow_entries_placement, placed = self.do_toy_placement(sfc)
      
    if placed:
      # self.sfcs[id] = sfc
      self.update_infrastructure_after_sfc(sfc, sfc_instance_id, vnfs_placement, flow_entries_placement)
    
    return placed    
  
  def do_toy_placement(self, sfc):
    # [0] -> because the placement node of source and destination are lists with just one element
    source = sfc.nodes['source']['placement_nodes'][0]
    destination = sfc.nodes['destination']['placement_nodes'][0]

    vnfs_placement = {} # vnf:node
    vnfs_placement['source'] = source

    flow_entries_placement = {} #flow entry: path
    
    last_vnf = 'source'

    for vnf_id in sfc.nodes:
      if sfc.nodes[vnf_id]['type'] != 'vnf':
        continue

      candidate_nodes = self.graph.get_nodes_by_resources(sfc.nodes[vnf_id]['resources'])

      if len(candidate_nodes) == 0:
        return sfc, {}, {}, False

      chosen = random.choice(candidate_nodes)
      vnfs_placement[vnf_id] = chosen

      path = nx.shortest_path(self.graph,source=source,target=chosen)
      flow_entries_placement[(last_vnf,vnf_id)] = [(path[i],path[i+1]) for i in range(len(path)-1)]

      # sfc.nodes[vnf_id]['placement_nodes'] = chosen
      sfc.nodes[vnf_id]['placement_nodes'].append(chosen)
      sfc.edges[(last_vnf,vnf_id)]['placement_link'] = flow_entries_placement[(last_vnf,vnf_id)]

      source = chosen
      last_vnf = vnf_id

    
    path = nx.shortest_path(self.graph,source=source,target=destination)
    flow_entries_placement[(last_vnf,'destination')] = [(path[i],path[i+1]) for i in range(len(path)-1)]

    sfc.edges[(last_vnf,'destination')]['placement_link'] = flow_entries_placement[(last_vnf,'destination')]

    vnfs_placement['destination'] = destination

    return sfc, vnfs_placement, flow_entries_placement, True


  def remove_sfc(self, sfc, sfc_id):
    for vnf_id in sfc.nodes:
      for node in sfc.nodes[vnf_id]['placement_nodes']:
        if sfc_id in self.graph.nodes[node]['placed']:
          self.graph.nodes[node]['placed'].pop(sfc_id)

      if sfc.nodes[vnf_id]['type'] == 'vnf':
        for item in self.nodes_components:
          for node in sfc.nodes[vnf_id]['placement_nodes']:
            self.graph.nodes[node]['available_resources'][item] += sfc.nodes[vnf_id]['resources'][item]
    
    for src_vnf,dst_vnf in sfc.edges:
      for src_flow_entry,dst_flow_entry in sfc.edges[src_vnf,dst_vnf]['placement_link']:
        for item in self.edges_components:
          self.graph.edges[(src_flow_entry,dst_flow_entry,0)]['available_resources'][item] += sfc.edges[src_vnf,dst_vnf]['resources'][item]

    # self.sfcs.pop(id)

  def get_vnfs_from_node(self, id):
    return self.graph.nodes[id]['placed']
  
  def set_nodes_edges_attributes(self, nodes_attr=None, edges_attr=None):
    if nodes_attr != None:
      nx.set_node_attributes(self.graph, nodes_attr)
    if edges_attr != None:  
      nx.set_edge_attributes(self.graph, edges_attr)
  
  def get_candidate_nodes(self, vnf_id, source, destination, vnf_requirements,
                          flow_entry_requirements, k, link_weight='delay', consider_src_dst=True):

    # selected_edges = [(u,v) for u,v,e in self.graph.edges(data=True) if e['resources']['bandwidth'] > flow_entry_requirements['bandwidth']]
    temp_graph = nx.Graph(((u,v,e) for u,v,e in self.graph.edges(data=True) if e['available_resources']['bandwidth'] >= flow_entry_requirements['bandwidth']))

    nodes_attrs = {node:self.graph.nodes[node] for node in self.graph.nodes if node in temp_graph.nodes}
    nx.set_node_attributes(temp_graph, nodes_attrs)


    for node in temp_graph.nodes:
      print(temp_graph.nodes[node])
    print('---------------')
    
    # nx.draw(temp_graph,with_labels=True)
    # plt.show()

    paths_lenghts = dict(nx.shortest_path_length(temp_graph,weight=link_weight))
    # paths_lenghts = nx.shortest_path_length(temp_graph,weight=link_weight)
    
    scores = {}
    
    # for node in self.graph.nodes:
    for node in temp_graph.nodes:

      if not consider_src_dst:
        if node == source or node == destination:
          continue
        
      if 'all' in temp_graph.nodes[node]['capabilities']['supported_VNFs']:
        meet_requeriment = True
      else:
        meet_requeriment = False
      
        # for vnf in self.graph.nodes[node]['capabilities']['supported_VNFs']:
        for vnf in temp_graph.nodes[node]['capabilities']['supported_VNFs']:
          if vnf_id == vnf['id']:
            meet_requeriment = True
            break

      if meet_requeriment:
        for req in vnf_requirements:
          # if self.graph.nodes[node]['available_resources'][req] < vnf_requirements[req]:
          # print(node,req,'resources',temp_graph.nodes[node]['available_resources'][req],'req',vnf_requirements[req])
          if temp_graph.nodes[node]['available_resources'][req] < vnf_requirements[req]:
            meet_requeriment = False
            break
        
      if meet_requeriment == False:
        continue

      scores[node] = paths_lenghts[node][source] + paths_lenghts[node][destination]
    
    scores = sorted(scores.items(), key=lambda item: item[1])
        
    if len(scores) < k:
      # print('se liga scores:',len(scores),'k:',k)
      scores += [(-(x+1),-1) for x in range(k-len(scores))]
      # print('total:',scores)
      # print('only k:',[node for node,score in scores][:k])
    
    # self.scores = scores[:k]
    return [node for node,score in scores][:k]

  def plot_candidate_nodes(self, source, destination, candidate_nodes, special_nodes=[]):
    
    # Get positions.
    # Here I use the spectral layout and add a little bit of noise.
    pos = nx.layout.spectral_layout(self.graph)
    pos = nx.spring_layout(self.graph, pos=pos, iterations=50)

    # Create position copies for shadows, and shift shadows
    pos_shadow = copy.deepcopy(pos)
    shift_amount = 0.006
    for idx in pos_shadow:
        pos_shadow[idx][0] += shift_amount
        pos_shadow[idx][1] -= shift_amount

    node_color = []
    for node in self.graph.nodes:
        if node in candidate_nodes and node not in special_nodes:
          node_color.append('#C70039') # pink  

        elif node == source or node == destination:
          node_color.append('#FF5733') # orange
        
        elif node in special_nodes:
          node_color.append('#F1C40F') # yellow

        else:
          node_color.append('#581845') # purple
          # node_color.append('#212F3C') # grey
    
    shortest_path = nx.shortest_path(self.graph, source, destination)
    shortest_path = [(shortest_path[x],shortest_path[x+1],0) for x in range(len(shortest_path)-1)]
    
    edge_colors = []
    edge_widths = []
    for src,dst,dir in self.graph.edges:
      if ((src,dst,dir) in shortest_path) or ((dst,src,dir) in shortest_path):
        edge_colors.append('#1C2833')
        edge_widths.append(2)
      else:        
        edge_colors.append('#7F8C8D')
        edge_widths.append(0.5)

    # TO PLOT THE SCORES
    # pos_attrs = {}
    # for node, coords in pos.items():
    #     pos_attrs[node] = (coords[0], coords[1] + 0.08)

    # custom_node_attrs = {}
    # for node in self.graph.nodes:
    #   custom_node_attrs[node] = ''
    #   for x,y in self.scores:
    #     if node == x:
    #       custom_node_attrs[node] += str(y)
    #       break   

    #~~~~~~~~~~~~
    # Draw graph
    #~~~~~~~~~~~~
    fig = plt.figure(frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    nx.draw_networkx_nodes(self.graph, pos_shadow, node_color='k', alpha=0.5,node_size=300)

    nx.draw(G=self.graph, pos=pos, node_color=node_color,linewidths=2, #edgecolors='grey',
            with_labels=True, font_color='white',font_size=14, node_size=300)
    
    nx.draw_networkx_edges(G=self.graph, pos=pos,edge_color=edge_colors, width=edge_widths)
    
    # nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs)

    plt.show()
  
  def plot_graph(self):
    # Get positions.
    # Here I use the spectral layout and add a little bit of noise.
    pos = nx.layout.spectral_layout(self.graph)
    pos = nx.spring_layout(self.graph, pos=pos, iterations=50)

    # Create position copies for shadows, and shift shadows
    pos_shadow = copy.deepcopy(pos)
    shift_amount = 0.006
    for idx in pos_shadow:
        pos_shadow[idx][0] += shift_amount
        pos_shadow[idx][1] -= shift_amount

    node_color = []
    for node in self.graph.nodes:
      node_color.append('#581845') # purple      
    
    edge_colors = []
    edge_widths = []
    for edge in self.graph.edges:
      edge_colors.append('#7F8C8D')
      edge_widths.append(0.5)

    
    #~~~~~~~~~~~~
    # Draw graph
    #~~~~~~~~~~~~
    fig = plt.figure(frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    nx.draw_networkx_nodes(self.graph, pos_shadow, node_color='k', alpha=0.5,node_size=300)

    nx.draw(G=self.graph, pos=pos, node_color=node_color,linewidths=2, #edgecolors='grey',
            with_labels=True, font_color='white',font_size=14, node_size=300)
    
    nx.draw_networkx_edges(G=self.graph, pos=pos,edge_color=edge_colors, width=edge_widths)
    
    # nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs)

    plt.show()
  
  def create_redundancy_map(self,block=4):
    
    nodes = list(self.graph.nodes)
    nodes = [nodes[x:x+block] for x in range(0, len(nodes), block)]
    
    bkp_nodes = copy.deepcopy(nodes)
    
    for x, nodes_list in enumerate(nodes):
      for i in range(len(nodes_list)):
        self.redundancy_map[nodes_list[i]] = bkp_nodes[x-1][i]
    
    # print(self.redundancy_map)

# ------------------------------------------------------------------------------------------

'''
# Creating an infrastructure graph
# graph_as = None
number_of_nodes = 50
infrastructure_graph = InfrastructureGraph(graph_as=graph_as,nodes_number=number_of_nodes,
                                  network_type='AS',latitude=19.99,longitude=73.78,
                                  lat_list=None, long_list=None,
                                  resources_ranges=resources_ranges,
                                  vnf_list=vnf_list, nodes_support_all_vnfs=True,
                                  add_fat_tree=False,
                                  servers_number_micro=2, servers_number=4,
                                  add_clusters=True)

print('Number of nodes:',infrastructure_graph.number_of_nodes())
print('Number of links:',infrastructure_graph.number_of_edges())

igh = InfrastructureGraphHandler(infrastructure_graph,5)

igh.plot_graph()

# Generating an SFC graph
sfc = nx.DiGraph()

sfc.add_nodes_from([(i,{'resources':{'cpu':1,'memory':1,'storage':1},'type':'vnf','placement_nodes':[]}) for i in range(3)])

source, destination = random.sample(list(infrastructure_graph.nodes),2)
source, destination =  14, 9#45, 38
# source, destination = 1, 18

sfc.add_nodes_from([
                    ('source',{'placement_nodes':[source],'type':'source'}),
                    ('destination',{'placement_nodes':[destination],'type':'destination'})
                    ])


for x in range(sfc.number_of_nodes()-3):
  sfc.add_edge(x, x+1,resources={'delay':1,'bandwidth':1})

sfc.add_edge('source',0,resources={'delay':1,'bandwidth':1})
sfc.add_edge(sfc.number_of_nodes()-3,'destination',resources={'delay':1,'bandwidth':1})

# nx.draw(sfc,with_labels=True)

# for n in igh.graph.edges:
#   print(n,igh.graph.edges[n]['available_resources'])


vnf_resources = {'cpu':1,'memory':1,'storage':1}

flow_entry_resources = {'delay':1,'bandwidth':1}

physical_node = random.choice(list(infrastructure_graph.nodes))

physical_links = nx.shortest_path(infrastructure_graph, source, physical_node)
physical_links = [(physical_links[n],physical_links[n+1]) for n in range(len(physical_links)-1)]

# adding the SFC
igh.add_sfc(sfc,'0_0')

# removing the SFC
igh.remove_sfc(sfc,'0_0')

# igh.reset_infrastructure()
# print('---------------')
# for n in igh.graph.nodes:
#   print(n,igh.graph.nodes[n]['available_resources'])

# nodes_attr = {physical_node: copy.deepcopy(infrastructure_graph.nodes[physical_node])}
# nodes_attr[physical_node]['status'] = 'failure'

# # print(physical_links[0][0],physical_links[0][1])
# edges_attr = {(physical_links[0][0],physical_links[0][1],0): infrastructure_graph.edges[(physical_links[0][0],physical_links[0][1],0)]}
# edges_attr[(physical_links[0][0],physical_links[0][1],0)]['customer'] = 'Guto'

# igh.set_nodes_edges_attributes(nodes_attr,edges_attr)

# igh.set_nodes_edges_attributes(nodes_attr)
# print(igh.graph.nodes[physical_node],igh.graph.edges[(physical_links[0][0],physical_links[0][1],0)])


# sfc_instance_id = '0_0'
vnf_id = 0
# vnf_resources = {'cpu':1,'memory':1,'storage':1}
# flow_entry_resources = {'bandwidth':1}

# # print(physical_node, physical_links)
# igh.update_infrastructure_after_vnf(sfc_instance_id, vnf_id, vnf_resources, flow_entry_resources,
                                      # physical_node, physical_links, False)

a = datetime.datetime.now()

k=4
candidate_nodes = igh.get_candidate_nodes(vnf_id,source,
                                          destination,
                                          vnf_resources,
                                          flow_entry_resources,k=k)
print('Time to run:',datetime.datetime.now()-a)

special_nodes = [9]
# igh.plot_candidate_nodes(source,destination,candidate_nodes,special_nodes)


# for node in infrastructure_graph.nodes:
#   print(node,igh.get_vnfs_from_node(node))
# igh.graph.print_nodes_status()
# igh.graph.print_edges_status() #'''