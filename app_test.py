
import psycopg2
import networkx as nx
import matplotlib.pyplot as plt
import config
import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go
import community as community_louvain
import matplotlib.cm as cm
import dash
import dash_cytoscape as cyto
from dash import html
from dash.dependencies import Input, Output
import pickle
import igraph as ig





# Load graph
G = nx.read_gexf("huge_graph.gexf")

# Debug: Print graph info
print(G)

# Create a Dash app
app = dash.Dash(__name__)

# Create a cytoscape graph
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=[
            {"data": {"id": str(node)}} for node in G.nodes()
        ] + [
            {"data": {"source": str(source), "target": str(target)}} for source, target in G.edges()
        ],
        layout={'name': 'circle'},
        style={'width': '100%', 'height': '400px'}
    ),
    html.P(id='cytoscape-output')
])

# Callback to display node ID when clicked
@app.callback(Output('cytoscape-output', 'children'), Input('cytoscape', 'tapNodeData'))
def display_tap_node(data):
    if data is None:
        return "Click on a node"
    return f"You clicked on node: {data['id']}"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)