import random
from pathlib import Path
import matplotlib.pyplot as plt
from pyvis.network import Network
import networkx as nx
import ffmpeg

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

random.seed(42)

nt = Network(height='700px', width='1500', directed=True)
nt.repulsion()

input_filename = 'input.yuv'
reference_file = 'reference.yuv'
compressed_file = 'compressed_file.mp4'
vmaf_model_path = '/path/to/vmaf/model.pkl'  # replace with the path to your VMAF model

compression_pipeline = """
(
    ffmpeg
    .input(input_filename, s='1920x1080', pix_fmt='yuv420p10le')
    .filter('bilateral', sigmaS=75, sigmaR=0.75)
    .filter('super2xsai', size='3840x2160')
    .output(compressed_file, vcodec='libx265', crf=25, format='mp4',
            pix_fmt='yuv420p', movflags='frag_keyframe+empty_moov')
    .run()
)
"""

vmaf_pipeline = """
vmaf_command = (
    ffmpeg
    .input(reference_file, s='3840x2160', pix_fmt='yuv420p10le')
    .input(compressed_file)
    .filter('libvmaf', model_path=vmaf_model_path)
    .run()
)
"""

nt.add_node(0, label=f'Input\ns="1920x1080"\npix_fmt="yuv420p10le"', group=1, shape='box', x=20, y=400, physics=False, font={"size": 12}, labelBreak=True)
nt.add_node(1, label=f'Super resolution\nsuper2xsai\nsize="3840x2160"', group=1, shape='box', physics=True, font={"size": 12}, labelBreak=True)
nt.add_node(2, label=f'Compression\npipe:\vcodec="libx265"\ncrf=25\nformat="rawvideo"\npix_fmt="yuv420p"', group=1, shape='box', physics=True, font={"size": 12}, labelBreak=True)
nt.add_node(3, label=f'Output\nformat="mp4"\nmovflags="frag_keyframe+empty_moov"', shape='box', group=1, physics=False, font={"size": 12}, labelBreak=True)
nt.add_node(4, label=f'VMAF Reference Input\ns="3840x2160"\npix_fmt="yuv420p10le"', group=2, shape='box', physics=False, font={"size": 12}, labelBreak=True)
nt.add_node(5, label=f'VMAF Test Input\ncompressed_file', group=2, shape='box', physics=True, font={"size": 12}, labelBreak=True)
nt.add_node(6, label=f'VMAF: libvmaf\nmodel_path=vmaf_model_path', group=2, shape='box', physics=False, font={"size": 12}, labelBreak=True)
nt.add_node(7, label=f'FFMPEG compression pipeline code:\n{compression_pipeline}', group=2, shape='box', physics=False, font={"size": 12}, labelBreak=True)
nt.add_node(8, label=f'FFMPEG VMAF pipeline code:\n{vmaf_pipeline}', group=2, shape='box', physics=False, font={"size": 12}, labelBreak=True)

nt.add_edge(0, 1, group=1)
nt.add_edge(1, 2, group=1)
nt.add_edge(2, 3, group=1)
nt.add_edge(4, 5, group=2)
nt.add_edge(5, 6, group=2)

# nt.show('html/nx.html', notebook=False)
nt.save_graph('html/nx.html')
