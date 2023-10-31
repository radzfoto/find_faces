import matplotlib.pyplot as plt
from pyvis.network import Network
import networkx as nx

# nx_graph = nx.cycle_graph(10)
# nx_graph.nodes[1]['title'] = 'Number 1'
# nx_graph.nodes[1]['group'] = 1
# nx_graph.nodes[3]['title'] = 'I belong to a different group!'
# nx_graph.nodes[3]['group'] = 10
# nx_graph.add_node(20, size=20, title='couple', group=2)
# nx_graph.add_node(21, size=15, title='couple', group=2)
# nx_graph.add_edge(20, 21, weight=5)
# nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)

# Create a directed graph
# nx_graph = nx.DiGraph()

# # Add edges (this will also add the nodes)
# nx_graph.add_edge('A', 'B', label='edge1')
# nx_graph.add_edge('B', 'C', label='edge2')
# nx_graph.add_edge('C', 'A', label='edge3')

nt = Network('1000px', '1920px', notebook=False)
# populates the nodes and edges data structures
# nt.from_nx(nx_graph)

nt = Network(height='800px', width='100%', directed=True)
nt.repulsion()

nt.add_node(0, label=f'Node 0', shape='circle', x=20, y=400, physics=False, font={"size": 10}, labelBreak=True)
for i in range(1,5):
    nt.add_node(i, size=60, label=f'Node {i}', shape='square', font={"size": 10}, labelBreak=True)
    nt.add_edge(i-1, i, label=f'Edge {i-1} -- {i}')
nt.add_node(5, label=f'Node 6', shape='circle', x=1000, y=400, physics=False, font={"size": 10}, labelBreak=True)
nt.add_edge(4,5, label='Edge 4-5')

# for node in nt.nodes:
#     node['shape'] = 'square'
#     node['labelBreak'] = True

# for i, node in enumerate(nt.nodes):
#     node['size'] = 10
#     node['size'] *= 4
#     node['label'] = f'Node {i}'

for i, edge in enumerate(nt.edges):
    edge['title'] = f'Edge {i}'

# Render the network using the template
# nt.show('html/nx.html', notebook=False)
nt.save_graph('html/nx.html')
# webbrowser.open('html/index.html', new=2)