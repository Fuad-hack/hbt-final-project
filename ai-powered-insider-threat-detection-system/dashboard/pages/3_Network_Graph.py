"""Network Graph — Interactive entity relationship visualization."""
import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data_loader import (
    get_enriched_scores, load_file_access, load_usb_usage, load_graph_features
)
from components.theme import apply_theme, section_title, glow_divider

st.set_page_config(page_title="Network Graph", page_icon="🕸️", layout="wide")
apply_theme()

scores = get_enriched_scores()
file_access = load_file_access()
usb_usage = load_usb_usage()
graph_features = load_graph_features()

st.markdown("# 🕸️ Network Graph")
st.markdown("*Interactive entity relationship graph — Users, Files, and Devices.*")
glow_divider()

# --- Build node attributes ---
attrs = {}
for _, row in scores.iterrows():
    anomaly = row['max_score']
    attrs[row['user']] = {
        'anomaly': anomaly,
        'red_team': int(row['is_red_team']),
        'risk_level': row['risk_level'],
        'high_risk': row['risk_level'] in ['High', 'Critical'] or int(row['is_red_team']) == 1
    }

# --- Build graph ---
G = nx.Graph()
for _, row in file_access.iterrows():
    G.add_edge(row['user'], row['file'], type='access')
for _, row in usb_usage.iterrows():
    G.add_edge(row['user'], row['device'], type='usb')

# --- At-risk subgraph ---
high_risk_nodes = {n for n, v in attrs.items() if v['high_risk']}
connected_nodes = set()
for node in high_risk_nodes:
    connected_nodes.add(node)
    if node in G:
        connected_nodes.update(G.neighbors(node))
subG = G.subgraph(connected_nodes).copy()

# --- Stats ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Graph Nodes", len(G.nodes()))
with col2:
    st.metric("Graph Edges", len(G.edges()))
with col3:
    st.metric("At-Risk Subgraph Nodes", len(subG.nodes()))
with col4:
    st.metric("High-Risk Users", len(high_risk_nodes))

st.markdown("<br>", unsafe_allow_html=True)

# --- Legend ---
st.markdown("""
<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#ff4757;"></div>
        <span style="color:#888;font-size:0.85rem;">Red Team User</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#ff6348;"></div>
        <span style="color:#888;font-size:0.85rem;">High Anomaly</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#ffa502;"></div>
        <span style="color:#888;font-size:0.85rem;">Elevated Anomaly</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#00d4ff;"></div>
        <span style="color:#888;font-size:0.85rem;">Normal User</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#2ed573;"></div>
        <span style="color:#888;font-size:0.85rem;">File</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width:14px;height:14px;border-radius:50%;background:#a55eea;"></div>
        <span style="color:#888;font-size:0.85rem;">USB Device</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PyVis Network ---
net = Network(height='700px', width='100%', notebook=False, bgcolor='#0a0a0f', font_color='#c0c0c0')
net.barnes_hut(gravity=-2000, central_gravity=0.1, spring_length=200,
               spring_strength=0.01, damping=0.85, overlap=1)
net.set_options('''
var options = {
  "physics": {
    "enabled": true,
    "stabilization": {"enabled": true, "fit": true, "iterations": 2500, "updateInterval": 50},
    "barnesHut": {
      "gravitationalConstant": -2000, "centralGravity": 0.1,
      "springLength": 200, "springConstant": 0.01,
      "damping": 0.85, "avoidOverlap": 1
    }
  }
}
''')

for node in subG.nodes():
    if node in attrs:
        a = attrs[node]
        if a['red_team']:
            color, size = '#ff4757', 30
        elif a['anomaly'] > 1.5:
            color, size = '#ff6348', 22
        elif a['anomaly'] > 1.0:
            color, size = '#ffa502', 18
        else:
            color, size = '#00d4ff', 14
        title = f"User: {node}<br>Anomaly: {a['anomaly']:.3f}<br>Risk: {a['risk_level']}<br>Red Team: {'Yes' if a['red_team'] else 'No'}"
    elif str(node).startswith('file'):
        color, size, title = '#2ed573', 8, f"File: {node}"
    elif str(node).startswith('usb'):
        color, size, title = '#a55eea', 10, f"Device: {node}"
    else:
        color, size, title = '#636e72', 8, str(node)
    net.add_node(node, label=str(node), color=color, size=size, title=title)

for u, v, d in subG.edges(data=True):
    edge_color = '#a55eea44' if d.get('type') == 'usb' else '#2ed57322'
    net.add_edge(u, v, color=edge_color)

graph_path = 'dashboard/graph.html'
net.save_graph(graph_path)
st.components.v1.html(open(graph_path, 'r', encoding='utf-8').read(), height=720, scrolling=False)

glow_divider()

# --- Centrality Leaderboard ---
section_title("Centrality Leaderboard")
col_deg, col_bet = st.columns(2)

gf = graph_features.sort_values('degree_centrality', ascending=False)
with col_deg:
    st.markdown("**Degree Centrality** — Activity level (connections)")
    st.dataframe(
        gf[['user', 'degree_centrality']].rename(
            columns={'user': 'User', 'degree_centrality': 'Degree Centrality'}),
        use_container_width=True, height=350,
        column_config={'Degree Centrality': st.column_config.NumberColumn(format="%.4f")}
    )

gf_b = graph_features.sort_values('betweenness_centrality', ascending=False)
with col_bet:
    st.markdown("**Betweenness Centrality** — Information flow control")
    st.dataframe(
        gf_b[['user', 'betweenness_centrality']].rename(
            columns={'user': 'User', 'betweenness_centrality': 'Betweenness Centrality'}),
        use_container_width=True, height=350,
        column_config={'Betweenness Centrality': st.column_config.NumberColumn(format="%.4f")}
    )
