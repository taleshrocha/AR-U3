import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import numpy as np

airports_br = st.session_state.airports_br
routes_br = st.session_state.routes_br
G_br = st.session_state.G_br

st.markdown("### Mapa Interativo - Clique em dois aeroportos para ver o menor número de conexões")

# Initialize session state for selected airports
if 'selected_airports' not in st.session_state:
    st.session_state.selected_airports = []

# Filter airports by minimum connections (degree > 1)
airport_degrees = dict(G_br.degree())
airports_br['Airport ID'] = airports_br['Airport ID'].astype(int)
degree_mapping = {int(k): v for k, v in airport_degrees.items()}

filtered_airports = airports_br[
    airports_br['Airport ID'].map(degree_mapping).fillna(0) > 1
].copy()

# Create the figure
fig = go.Figure()

# Calculate marker sizes based on connections
degrees = [degree_mapping.get(aid, 0) for aid in filtered_airports['Airport ID']]
marker_sizes = []
for deg in degrees:
    if deg <= 10:
        size = max(6, 6 + deg * 0.75)
    else:
        size = max(12, min(30, 12 + (deg - 10) * 0.25))
    marker_sizes.append(size)

# Determine colors based on selection
colors = []
for aid in filtered_airports['Airport ID']:
    if aid in st.session_state.selected_airports:
        colors.append('#0000FF')  # Bright blue
    else:
        colors.append('#87CEEB')  # Light blue

# Add airports
fig.add_trace(go.Scattergeo(
    lon=filtered_airports['Longitude'],
    lat=filtered_airports['Latitude'],
    text=filtered_airports['IATA'],
    customdata=filtered_airports['Airport ID'],
    mode='markers+text',
    textfont=dict(size=12, color='#000000'),
    textposition="top center",
    marker=dict(
        size=marker_sizes,
        color=colors,
        line=dict(width=3, color='#000000')
    ),
    name='Aeroportos',
    hovertemplate='<b>%{text}</b><br>Conexões: ' + 
                  filtered_airports['Airport ID'].map(degree_mapping).astype(str) + 
                  '<extra></extra>'
))

# Add all routes in gray
filtered_airport_ids = set(filtered_airports['Airport ID'])
filtered_routes = routes_br[
    routes_br['Source airport ID'].isin(filtered_airport_ids) &
    routes_br['Destination airport ID'].isin(filtered_airport_ids)
]

for _, row in filtered_routes.iterrows():
    src = airports_br[airports_br['Airport ID'] == row['Source airport ID']]
    dst = airports_br[airports_br['Airport ID'] == row['Destination airport ID']]
    if not src.empty and not dst.empty:
        fig.add_trace(go.Scattergeo(
            lon=[src.iloc[0]['Longitude'], dst.iloc[0]['Longitude']],
            lat=[src.iloc[0]['Latitude'], dst.iloc[0]['Latitude']],
            mode='lines',
            line=dict(width=1, color='rgba(128,128,128,0.4)'),
            showlegend=False,
            hoverinfo='none'
        ))

# If two airports are selected, show shortest path
if len(st.session_state.selected_airports) == 2:
    src_id, dst_id = st.session_state.selected_airports
    try:
        path = nx.shortest_path(G_br, source=src_id, target=dst_id)
        
        # Add shortest path markers
        path_lons = [airports_br.loc[airports_br["Airport ID"] == i, "Longitude"].values[0] for i in path]
        path_lats = [airports_br.loc[airports_br["Airport ID"] == i, "Latitude"].values[0] for i in path]
        path_codes = [airports_br.loc[airports_br["Airport ID"] == i, "IATA"].values[0] for i in path]
        
        fig.add_trace(go.Scattergeo(
            lon=path_lons,
            lat=path_lats,
            mode='markers+text',
            marker=dict(size=16, color='#0000FF', symbol='star', line=dict(width=3, color='#000000')),
            text=path_codes,
            textposition="top center",
            textfont=dict(size=14, color='#000000'),
            name='Menor Número de Conexões',
            showlegend=True
        ))
        
        # Add shortest path lines
        for i in range(len(path) - 1):
            src = airports_br[airports_br["Airport ID"] == path[i]]
            dst = airports_br[airports_br["Airport ID"] == path[i+1]]
            fig.add_trace(go.Scattergeo(
                lon=[src.iloc[0]["Longitude"], dst.iloc[0]["Longitude"]],
                lat=[src.iloc[0]["Latitude"], dst.iloc[0]["Latitude"]],
                mode='lines',
                line=dict(width=6, color='#0000FF'),
                showlegend=False,
                hoverinfo='none'
            ))
        
        # Show path info
        src_name = airports_br.loc[airports_br["Airport ID"] == src_id, "Name"].values[0]
        dst_name = airports_br.loc[airports_br["Airport ID"] == dst_id, "Name"].values[0]
        st.success(f"Menor caminho encontrado: {len(path)-1} conexões entre {src_name} e {dst_name}")
        
    except nx.NetworkXNoPath:
        st.error("Não existe caminho entre os aeroportos selecionados.")

# Layout
fig.update_layout(
    title={
        'text': f'Rede Aérea Brasileira - Menor Número de Conexões',
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

# Display the plot and capture clicks
clicked_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

# Handle click events
if clicked_data and 'selection' in clicked_data and clicked_data['selection']['points']:
    point = clicked_data['selection']['points'][0]
    if 'customdata' in point:
        clicked_airport_id = int(point['customdata'])
        
        if clicked_airport_id not in st.session_state.selected_airports:
            st.session_state.selected_airports.append(clicked_airport_id)
            if len(st.session_state.selected_airports) > 2:
                st.session_state.selected_airports = st.session_state.selected_airports[-2:]
        st.rerun()

# Control panel
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Limpar Seleção"):
        st.session_state.selected_airports = []
        st.rerun()

with col2:
    st.metric("Aeroportos Selecionados", len(st.session_state.selected_airports))

with col3:
    st.metric("Total de Aeroportos", len(filtered_airports))

# Show selected airports
if st.session_state.selected_airports:
    st.markdown("**Aeroportos Selecionados:**")
    for i, airport_id in enumerate(st.session_state.selected_airports):
        airport_info = airports_br[airports_br['Airport ID'] == airport_id].iloc[0]
        st.write(f"{i+1}. {airport_info['Name']} ({airport_info['IATA']})")
