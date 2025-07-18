import streamlit as st
import plotly.graph_objects as go
import numpy as np

airports_br = st.session_state.airports_br
routes_br = st.session_state.routes_br

st.markdown("## Mapa Rotas Aéreas")

# Interactive controls
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    show_routes = st.checkbox("Mostrar Rotas", value=True)
    route_opacity = st.slider("Opacidade das Rotas", 0.1, 1.0, 0.1, 0.1)

with col2:
    min_connections = st.slider("Mín. Conexões por Aeroporto", 0, 80, 1)

with col3:
    color_by_degree = st.checkbox("Colorir por Grau de Conectividade", value=True)
    show_labels = st.checkbox("Mostrar Labels", value=False)

# Filter airports by minimum connections
G_br = st.session_state.G_br
airport_degrees = dict(G_br.degree())

# Ensure Airport ID is integer type for proper mapping
airports_br['Airport ID'] = airports_br['Airport ID'].astype(int)

# Create a mapping with consistent integer keys
degree_mapping = {int(k): v for k, v in airport_degrees.items()}

filtered_airports = airports_br[
    airports_br['Airport ID'].map(degree_mapping).fillna(0) >= min_connections
].copy()

# Create enhanced plotly figure
fig = go.Figure()

# Add airports with degree-based coloring
if color_by_degree and not filtered_airports.empty:
    degrees = [degree_mapping.get(aid, 0) for aid in filtered_airports['Airport ID']]
    colors = degrees
    colorbar_title = "Grau de Conectividade"
else:
    colors = '#1f77b4'  # Light blue instead of 'blue'
    colorbar_title = None

# Calculate marker sizes based on connections (degree)
degrees = [degree_mapping.get(aid, 0) for aid in filtered_airports['Airport ID']]
marker_sizes = []
for deg in degrees:
    if deg <= 10:
        size = max(3, 3 + deg * 0.75)  # Linear scaling for low degrees (3-10)
    else:
        size = max(10, min(25, 10 + (deg - 10) * 0.25))  # Reduced scaling for high degrees (10-25)
    marker_sizes.append(size)

fig.add_trace(go.Scattergeo(
    lon=filtered_airports['Longitude'],
    lat=filtered_airports['Latitude'],
    text=filtered_airports['Name'] + '<br>Conexões: ' + filtered_airports['Airport ID'].map(degree_mapping).fillna(0).astype(str),
    mode='markers+text' if show_labels else 'markers',
    textfont=dict(size=8, color='#000000'),
    textposition="top center",
    marker=dict(
        size=marker_sizes,
        color=colors,
        colorscale='Blues' if color_by_degree else None,
        colorbar=dict(
            title=dict(text=colorbar_title, font=dict(color='#000000')),
            tickfont=dict(color='#000000')
        ) if color_by_degree else None,
        showscale=color_by_degree,
        line=dict(width=2, color='#000000')
    ),
    name='Aeroportos',
    hovertemplate='<b>%{text}</b><extra></extra>'
))

# Add routes if enabled
if show_routes:
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
                line=dict(width=1.2, color=f'rgba(0,0,0,{route_opacity})'),
                showlegend=False,
                hoverinfo='none'
            ))

# Enhanced layout
fig.update_layout(
    title={
        'text': f'Rede Aérea Brasileira - {len(filtered_airports)} Aeroportos',
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

st.plotly_chart(fig, use_container_width=True)

# Statistics panel
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Aeroportos Filtrados", len(filtered_airports))
with col2:
    st.metric("Total de Rotas", len(routes_br))
with col3:
    if not filtered_airports.empty:
        avg_degree = np.mean([degree_mapping.get(aid, 0) for aid in filtered_airports['Airport ID']])
        st.metric("Conectividade Média", f"{avg_degree:.1f}")
with col4:
    if degree_mapping:
        max_connections = max(degree_mapping.values())
        busiest = [name for aid, name in zip(airports_br['Airport ID'], airports_br['Name']) 
                  if degree_mapping.get(aid, 0) == max_connections]
        st.metric("Mais Conectado", busiest[0] if busiest else "N/A")
