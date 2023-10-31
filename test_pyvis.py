import webbrowser
from pyvis.network import Network
import networkx as nx
nx_graph = nx.cycle_graph(10)
nx_graph.nodes[1]['title'] = 'Number 1'
nx_graph.nodes[1]['group'] = 1
nx_graph.nodes[3]['title'] = 'I belong to a different group!'
nx_graph.nodes[3]['group'] = 10
nx_graph.add_node(20, size=20, title='couple', group=2)
nx_graph.add_node(21, size=15, title='couple', group=2)
nx_graph.add_edge(20, 21, weight=5)
nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)
nt = Network('500px', '500px', notebook=False)
# populates the nodes and edges data structures
nt.from_nx(nx_graph)

for node in nt.nodes:
    node['shape'] = 'square'

for i, node in enumerate(nt.nodes):
    node['size'] *= 4
    node['label'] = f'Node {i}'

for i, edge in enumerate(nt.edges):
    edge['title'] = f'Edge {i}'

# Render the network using the template
# nt.show('html/nx.html', notebook=False)
nt.save_graph('html/nx.html')

# webbrowser.open('html/index.html', new=2)