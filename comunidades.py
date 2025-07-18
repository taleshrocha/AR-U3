import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import community as community_louvain
import numpy as np
import pandas as pd

st.markdown("## Análise de Comunidades na Rede Aérea Brasileira")

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br

# Simplified interactive controls
min_connections = st.slider("Mínimo de Conexões por Aeroporto", 0, 20, 1)

# Filter airports by minimum connections
airport_degrees = dict(G_br.degree())
filtered_nodes = [node for node, degree in airport_degrees.items() if degree >= min_connections]
G_filtered = G_br.subgraph(filtered_nodes).copy()

if len(G_filtered.nodes()) == 0:
    st.error("Nenhum aeroporto atende aos critérios de filtro.")
    st.stop()

# Convert to undirected and find communities
G_undirected = G_filtered.to_undirected()
partition = community_louvain.best_partition(G_undirected)

# Calculate modularity
modularity = community_louvain.modularity(partition, G_undirected)

# Get community information
communities = {}
for node, comm_id in partition.items():
    if comm_id not in communities:
        communities[comm_id] = []
    communities[comm_id].append(node)

# Create comprehensive dataframe with community information
community_data = []
for node_id in G_undirected.nodes():
    airport_info = airports_br[airports_br['Airport ID'] == node_id]
    if not airport_info.empty:
        community_data.append({
            'Airport_ID': node_id,
            'IATA': airport_info.iloc[0]['IATA'],
            'Name': airport_info.iloc[0]['Name'],
            'City': airport_info.iloc[0]['City'],
            'Latitude': airport_info.iloc[0]['Latitude'],
            'Longitude': airport_info.iloc[0]['Longitude'],
            'Community': partition[node_id],
            'Connections': G_undirected.degree(node_id)
        })

df_communities = pd.DataFrame(community_data)

# Create color palette for communities
colors = px.colors.qualitative.Set3
if len(communities) > len(colors):
    colors = colors * (len(communities) // len(colors) + 1)

# Create the map
fig = go.Figure()

# Add each community as a separate trace
for i, (comm_id, nodes) in enumerate(communities.items()):
    comm_data = df_communities[df_communities['Community'] == comm_id]
    
    # Calculate marker sizes based on connections (range: 8-25)
    connections = comm_data['Connections'].values
    min_conn = connections.min()
    max_conn = connections.max()
    
    if max_conn > min_conn:
        normalized_connections = (connections - min_conn) / (max_conn - min_conn)
    else:
        normalized_connections = np.ones_like(connections)
    
    marker_sizes = 8 + normalized_connections * 17
    
    # Create hover text
    hover_text = []
    for _, row in comm_data.iterrows():
        hover_text.append(
            f"<b>{row['Name']}</b><br>"
            f"IATA: {row['IATA']}<br>"
            f"Cidade: {row['City']}<br>"
            f"Comunidade: {row['Community']}<br>"
            f"Conexões: {row['Connections']}"
        )
    
    fig.add_trace(go.Scattergeo(
        lon=comm_data['Longitude'],
        lat=comm_data['Latitude'],
        text=comm_data['IATA'],
        mode='markers+text',
        textfont=dict(size=10, color='#000000'),
        textposition="top center",
        marker=dict(
            size=marker_sizes,
            color=colors[i % len(colors)],
            line=dict(width=1.5, color='#000000'),
            opacity=0.8
        ),
        name=f'Comunidade {comm_id} ({len(nodes)} aeroportos)',
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text
    ))

# Update geo layout
fig.update_geos(
    scope='south america',
    projection_type='natural earth',
    showland=True,
    landcolor='rgb(240, 240, 240)',
    coastlinecolor='rgb(100, 100, 100)',
    showocean=True,
    oceancolor='rgb(255, 255, 255)',
    showcountries=True,
    countrycolor='rgb(100, 100, 100)',
    center=dict(lat=-15, lon=-55),
    projection_scale=1.3
)

# Update layout
fig.update_layout(
    title={
        'text': f'Comunidades na Rede Aérea Brasileira<br><sub>{len(communities)} comunidades encontradas - Modularidade: {modularity:.3f}</sub>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'color': '#000000', 'size': 20}
    },
    height=800,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#000000'),
    legend=dict(
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#000000',
        borderwidth=1,
        font=dict(color='#000000')
    )
)

st.plotly_chart(fig, use_container_width=True)

# Display statistics
st.markdown("### Estatísticas das Comunidades")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Número de Comunidades", len(communities))
with col2:
    st.metric("Modularidade", f"{modularity:.3f}")
with col3:
    st.metric("Aeroportos Analisados", len(G_filtered.nodes()))
with col4:
    avg_size = np.mean([len(comm) for comm in communities.values()])
    st.metric("Tamanho Médio das Comunidades", f"{avg_size:.1f}")

# Display community details
st.markdown("### Detalhes das Comunidades")

# Sort communities by size
sorted_communities = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)

for i, (comm_id, nodes) in enumerate(sorted_communities[:10]):  # Show top 10 communities
    with st.expander(f"Comunidade {comm_id} ({len(nodes)} aeroportos)"):
        
        # Show airports in this community
        airport_list = []
        for node in nodes:
            if node in airport_info:
                info = airport_info[node]
                degree = G_undirected.degree(node)
                airport_list.append({
                    'IATA': info['iata'],
                    'Nome': info['name'],
                    'Conexões': degree,
                    'ID': node
                })
            else:
                airport_list.append({
                    'IATA': 'N/A',
                    'Nome': f'Aeroporto {node}',
                    'Conexões': G_undirected.degree(node),
                    'ID': node
                })
        
        # Sort by connections
        airport_list.sort(key=lambda x: x['Conexões'], reverse=True)
        
        # Display as table with explicit styling
        if airport_list:
            df_display = pd.DataFrame(airport_list)
            st.markdown("""
            <style>
            .stDataFrame {
                background-color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)
            st.dataframe(df_display, use_container_width=True)
        
        # Community statistics
        degrees_in_comm = [G_undirected.degree(node) for node in nodes]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Aeroporto Mais Conectado", 
                     f"{max(degrees_in_comm)} conexões")
        with col2:
            st.metric("Conectividade Média", 
                     f"{np.mean(degrees_in_comm):.1f}")
        with col3:
            # Calculate internal vs external edges
            internal_edges = 0
            external_edges = 0
            for node in nodes:
                for neighbor in G_undirected.neighbors(node):
                    if neighbor in nodes:
                        internal_edges += 1
                    else:
                        external_edges += 1
            internal_edges //= 2  # Each edge counted twice
            
            if internal_edges + external_edges > 0:
                internal_ratio = internal_edges / (internal_edges + external_edges)
                st.metric("Coesão Interna", f"{internal_ratio:.2f}")
            else:
                st.metric("Coesão Interna", "N/A")