import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import community as community_louvain
import matplotlib.cm as cm
import numpy as np

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

# Create airport ID to info mapping
airports_br['Airport ID'] = airports_br['Airport ID'].astype(int)
airport_info = {row['Airport ID']: {'name': row['Name'], 'iata': row['IATA']} 
                for _, row in airports_br.iterrows()}

# Create visualization
colors = [partition[n] for n in G_undirected.nodes()]
pos = nx.spring_layout(G_undirected, seed=42)

# Calculate node sizes based on degree
degrees = [G_undirected.degree(n) for n in G_undirected.nodes()]
node_sizes = [max(20, deg * 10) for deg in degrees]

fig, ax = plt.subplots(figsize=(12, 10))

# Draw network
nx.draw_networkx_edges(G_undirected, pos, alpha=0.3, width=0.5, ax=ax)
nodes = nx.draw_networkx_nodes(G_undirected, pos, 
                              node_color=colors, 
                              cmap=cm.get_cmap('tab10'),
                              node_size=node_sizes,
                              alpha=0.8, ax=ax)

# Always show IATA labels
labels = {}
for node in G_undirected.nodes():
    if node in airport_info:
        labels[node] = airport_info[node]['iata']
    else:
        labels[node] = str(node)
nx.draw_networkx_labels(G_undirected, pos, labels, font_size=8, ax=ax)

ax.set_title(f"Comunidades (Louvain) - {len(communities)} comunidades encontradas\n"
            f"Modularidade: {modularity:.3f}")
ax.axis('off')

st.pyplot(fig)

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
        
        # Display as table
        if airport_list:
            st.dataframe(airport_list, use_container_width=True)
        
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