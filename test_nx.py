import matplotlib.pyplot as plt
import networkx as nx

G = nx.DiGraph()

# Add edges (this will also add the nodes)
G.add_edge('A', 'B', label='edge1')
G.add_edge('B', 'C', label='edge2')
G.add_edge('C', 'A', label='edge3')

pos = nx.spring_layout(G)

nx.draw(G, pos, with_labels=True, node_size=2000, node_shape='s', node_color='lightblue', font_size=10, font_weight='bold')

plt.show()