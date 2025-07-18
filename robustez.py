import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import numpy as np

st.markdown("## Análise de Robustez da Rede Aérea Brasileira")

# Initialize session state for removed nodes
if 'removed_nodes' not in st.session_state:
    st.session_state.removed_nodes = set()

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br
routes_br = st.session_state.routes_br

# Create a copy of the original graph and remove selected nodes
G_current = G_br.copy()
for node in st.session_state.removed_nodes:
    if node in G_current:
        G_current.remove_node(node)

# Convert to undirected for robustness analysis
G_undirected = G_current.to_undirected()

# Calculate robustness metrics
def calculate_metrics(graph):
    if len(graph.nodes()) == 0:
        return {
            'nodes': 0,
            'edges': 0,
            'components': 0,
            'largest_component': 0,
            'avg_clustering': 0
        }
    
    # Basic metrics
    num_nodes = len(graph.nodes())
    num_edges = len(graph.edges())
    
    # Connected components
    components = list(nx.connected_components(graph))
    num_components = len(components)
    largest_component_size = len(max(components, key=len)) if components else 0
    
    # Clustering coefficient
    avg_clustering = nx.average_clustering(graph) if num_nodes > 0 else 0
    
    return {
        'nodes': num_nodes,
        'edges': num_edges,
        'components': num_components,
        'largest_component': largest_component_size,
        'avg_clustering': avg_clustering
    }

# Calculate metrics for current state
current_metrics = calculate_metrics(G_undirected)
original_metrics = calculate_metrics(G_br.to_undirected())

# Control panel
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    removal_strategy = st.selectbox(
        "Estratégia de Remoção:",
        ["Manual (clique no mapa)", "Por Grau (mais conectados)", "Aleatória"]
    )

with col2:
    if removal_strategy == "Por Grau (mais conectados)":
        num_remove = st.number_input("Número de nós a remover:", 1, 10, 1)
        if st.button("Remover Nós por Grau"):
            # Get nodes by degree and remove top ones
            degrees = dict(G_br.degree())
            # Filter out already removed nodes
            available_nodes = {k: v for k, v in degrees.items() if k not in st.session_state.removed_nodes}
            if available_nodes:
                top_nodes = sorted(available_nodes.items(), key=lambda x: x[1], reverse=True)[:num_remove]
                for node, _ in top_nodes:
                    st.session_state.removed_nodes.add(node)
                st.rerun()
    
    elif removal_strategy == "Aleatória":
        num_remove = st.number_input("Número de nós a remover:", 1, 10, 1)
        if st.button("Remover Nós Aleatoriamente"):
            available_nodes = [n for n in G_br.nodes() if n not in st.session_state.removed_nodes]
            if available_nodes:
                to_remove = np.random.choice(available_nodes, 
                                           size=min(num_remove, len(available_nodes)), 
                                           replace=False)
                for node in to_remove:
                    st.session_state.removed_nodes.add(node)
                st.rerun()

with col3:
    if st.button("Restaurar Rede Original"):
        st.session_state.removed_nodes = set()
        st.rerun()

# Display metrics comparison
st.markdown("### Impacto na Robustez da Rede")

col1, col2, col3 = st.columns(3)

with col1:
    airports_remaining = current_metrics['nodes']
    airports_removed = len(st.session_state.removed_nodes)
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; text-align: center;">
        <div style="color: #666; font-size: 14px; margin-bottom: 0.5rem;">Aeroportos Restantes</div>
        <div style="color: black; font-size: 24px; font-weight: 600;">{airports_remaining}</div>
        <div style="color: #d32f2f; font-size: 12px;">(-{airports_removed})</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    routes_remaining = current_metrics['edges']
    original_routes = original_metrics['edges']
    routes_removed = original_routes - routes_remaining
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; text-align: center;">
        <div style="color: #666; font-size: 14px; margin-bottom: 0.5rem;">Rotas Restantes</div>
        <div style="color: black; font-size: 24px; font-weight: 600;">{routes_remaining}</div>
        <div style="color: #d32f2f; font-size: 12px;">(-{routes_removed})</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    largest_comp_ratio = current_metrics['largest_component'] / original_metrics['largest_component'] if original_metrics['largest_component'] > 0 else 0
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; text-align: center;">
        <div style="color: #666; font-size: 14px; margin-bottom: 0.5rem;">Maior Componente</div>
        <div style="color: black; font-size: 24px; font-weight: 600;">{current_metrics['largest_component']}</div>
        <div style="color: {'#d32f2f' if largest_comp_ratio < 0.8 else '#388e3c'}; font-size: 12px;">{largest_comp_ratio:.1%}</div>
    </div>
    """, unsafe_allow_html=True)

# Create the map
st.markdown("### Mapa Interativo da Rede")
if removal_strategy == "Manual (clique no mapa)":
    st.markdown("**Clique nos aeroportos no mapa para removê-los da rede**")

fig = go.Figure()

# Filter airports to show only those still in the network
remaining_airports = airports_br[~airports_br['Airport ID'].isin(st.session_state.removed_nodes)].copy()
removed_airports = airports_br[airports_br['Airport ID'].isin(st.session_state.removed_nodes)].copy()

# Calculate degrees for remaining airports
current_degrees = dict(G_current.degree())

# Add remaining airports
if not remaining_airports.empty:
    degrees = [current_degrees.get(aid, 0) for aid in remaining_airports['Airport ID']]
    
    # Calculate marker sizes
    marker_sizes = []
    for deg in degrees:
        if deg == 0:
            size = 5
        elif deg <= 10:
            size = max(6, 6 + deg * 0.75)
        else:
            size = max(12, min(30, 12 + (deg - 10) * 0.25))
        marker_sizes.append(size)
    
    # Color by degree
    colors = degrees
    
    fig.add_trace(go.Scattergeo(
        lon=remaining_airports['Longitude'],
        lat=remaining_airports['Latitude'],
        text=remaining_airports['IATA'],
        customdata=remaining_airports['Airport ID'],
        mode='markers+text',
        textfont=dict(size=10, color='#000000'),
        textposition="top center",
        marker=dict(
            size=marker_sizes,
            color=colors,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(
                title=dict(text="Conexões", font=dict(color='#000000')),
                tickfont=dict(color='#000000')
            ),
            line=dict(width=2, color='#000000')
        ),
        name='Aeroportos Ativos',
        hovertemplate='<b>%{text}</b><br>Conexões: ' + 
                      remaining_airports['Airport ID'].map(current_degrees).fillna(0).astype(str) + 
                      '<extra></extra>'
    ))

# Add removed airports in red
if not removed_airports.empty:
    fig.add_trace(go.Scattergeo(
        lon=removed_airports['Longitude'],
        lat=removed_airports['Latitude'],
        text=removed_airports['IATA'],
        customdata=removed_airports['Airport ID'],
        mode='markers+text',
        textfont=dict(size=10, color='#000000'),
        textposition="top center",
        marker=dict(
            size=15,
            color='#ff0000',
            symbol='x',
            line=dict(width=3, color='#000000')
        ),
        name='Aeroportos Removidos',
        hovertemplate='<b>%{text}</b><br>REMOVIDO<extra></extra>'
    ))

# Add routes for remaining network
if not remaining_airports.empty:
    remaining_airport_ids = set(remaining_airports['Airport ID'])
    remaining_routes = routes_br[
        routes_br['Source airport ID'].isin(remaining_airport_ids) &
        routes_br['Destination airport ID'].isin(remaining_airport_ids)
    ]
    
    for _, row in remaining_routes.iterrows():
        src = airports_br[airports_br['Airport ID'] == row['Source airport ID']]
        dst = airports_br[airports_br['Airport ID'] == row['Destination airport ID']]
        if not src.empty and not dst.empty:
            fig.add_trace(go.Scattergeo(
                lon=[src.iloc[0]['Longitude'], dst.iloc[0]['Longitude']],
                lat=[src.iloc[0]['Latitude'], dst.iloc[0]['Latitude']],
                mode='lines',
                line=dict(width=1, color='rgba(0,100,200,0.3)'),
                showlegend=False,
                hoverinfo='none'
            ))

# Update layout
fig.update_layout(
    title={
        'text': f'Análise de Robustez - {len(remaining_airports)} aeroportos ativos',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'color': '#000000', 'size': 20}
    },
    geo=dict(
        scope='south america',
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(240, 240, 240)',
        coastlinecolor='rgb(0, 0, 0)',
        showocean=True,
        oceancolor='rgb(255, 255, 255)',
        showcountries=True,
        countrycolor='rgb(0, 0, 0)',
        center=dict(lat=-15, lon=-55),
        projection_scale=1.2
    ),
    height=700,
    showlegend=True,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#000000')
)

# Handle map clicks for manual removal
if removal_strategy == "Manual (clique no mapa)":
    clicked_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    
    if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
        point = clicked_data['selection']['points'][0]
        if 'customdata' in point:
            clicked_airport_id = int(point['customdata'])
            
            # Only remove if not already removed
            if clicked_airport_id not in st.session_state.removed_nodes:
                st.session_state.removed_nodes.add(clicked_airport_id)
                st.rerun()
else:
    st.plotly_chart(fig, use_container_width=True)

# Show removed airports list
if st.session_state.removed_nodes:
    st.markdown("### Aeroportos Removidos")
    removed_list = []
    for node_id in st.session_state.removed_nodes:
        airport_info = airports_br[airports_br['Airport ID'] == node_id]
        if not airport_info.empty:
            removed_list.append({
                'IATA': airport_info.iloc[0]['IATA'],
                'Nome': airport_info.iloc[0]['Name'],
                'Cidade': airport_info.iloc[0]['City']
            })
    
    if removed_list:
        df_removed = pd.DataFrame(removed_list)
        st.dataframe(df_removed, use_container_width=True, hide_index=True)
