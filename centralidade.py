import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import pandas as pd
import numpy as np

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br

st.markdown("## Análise Avançada de Centralidade")

with st.spinner("Processando..."):
    degree_cent = nx.degree_centrality(G_br)
    betweenness_cent = nx.betweenness_centrality(G_br, k=min(50, len(G_br)))  # Sample for performance
    closeness_cent = nx.closeness_centrality(G_br)
    eigenvector_cent = nx.eigenvector_centrality(G_br, max_iter=1000)

# Create comprehensive dataframe
centrality_data = []
for node_id in G_br.nodes():
    airport_info = airports_br[airports_br['Airport ID'] == node_id]
    if not airport_info.empty:
        centrality_data.append({
            'Airport_ID': node_id,
            'IATA': airport_info.iloc[0]['IATA'],
            'Name': airport_info.iloc[0]['Name'],
            'City': airport_info.iloc[0]['City'],
            'Latitude': airport_info.iloc[0]['Latitude'],
            'Longitude': airport_info.iloc[0]['Longitude'],
            'Degree_Centrality': degree_cent[node_id],
            'Betweenness_Centrality': betweenness_cent[node_id],
            'Closeness_Centrality': closeness_cent[node_id],
            'Eigenvector_Centrality': eigenvector_cent[node_id]
        })

df_centrality = pd.DataFrame(centrality_data)

# Define centrality metrics
centrality_metrics = [
    ('Degree_Centrality', 'Degree Centrality'),
    ('Betweenness_Centrality', 'Betweenness Centrality'),
    ('Closeness_Centrality', 'Closeness Centrality'),
    ('Eigenvector_Centrality', 'Eigenvector Centrality')
]

# Create subplots with 2x2 layout
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[title for _, title in centrality_metrics],
    specs=[[{"type": "geo"}, {"type": "geo"}],
           [{"type": "geo"}, {"type": "geo"}]],
    vertical_spacing=0.12,
    horizontal_spacing=0.05
)

# Color scales for each metric
color_scales = ['Viridis', 'Plasma', 'Cividis', 'Turbo']

for idx, ((metric, title), colorscale) in enumerate(zip(centrality_metrics, color_scales)):
    row = (idx // 2) + 1
    col = (idx % 2) + 1
    
    # Get centrality values and normalize them
    centrality_values = df_centrality[metric].values
    min_cent = centrality_values.min()
    max_cent = centrality_values.max()
    
    # Calculate marker sizes based on centrality (range: 4-30)
    normalized_centrality = (centrality_values - min_cent) / (max_cent - min_cent) if max_cent > min_cent else np.ones_like(centrality_values)
    marker_sizes = 4 + normalized_centrality * 26
    
    # Calculate opacity based on centrality (range: 0.3-1.0)
    marker_opacity = 0.3 + normalized_centrality * 0.7
    
    # Get top 5 airports for labels
    top_airports = df_centrality.nlargest(5, metric)
    top_airport_ids = set(top_airports['Airport_ID'])
    
    # Create hover text
    hover_text = []
    for _, row_data in df_centrality.iterrows():
        hover_text.append(
            f"<b>{row_data['Name']}</b><br>"
            f"IATA: {row_data['IATA']}<br>"
            f"Cidade: {row_data['City']}<br>"
            f"{title}: {row_data[metric]:.4f}"
        )
    
    # Add airports trace
    fig.add_trace(go.Scattergeo(
        lon=df_centrality['Longitude'],
        lat=df_centrality['Latitude'],
        text=[row_data['IATA'] if row_data['Airport_ID'] in top_airport_ids else '' 
              for _, row_data in df_centrality.iterrows()],
        mode='markers+text',
        textfont=dict(size=10, color='#000000'),
        textposition="top center",
        marker=dict(
            size=marker_sizes,
            color=centrality_values,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                title=dict(text=title, font=dict(color='#000000', size=12)),
                tickfont=dict(color='#000000', size=10),
                len=0.35,
                x=1.02 if col == 2 else -0.02,
                y=0.75 if row == 1 else 0.25,
                thickness=15
            ),
            line=dict(width=1.5, color='#000000'),
            opacity=marker_opacity,
            cmin=min_cent,
            cmax=max_cent
        ),
        name=f'Aeroportos - {title}',
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text,
        showlegend=False
    ), row=row, col=col)

# Update geo layout for each subplot
geo_config = dict(
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

fig.update_geos(geo_config)

# Update layout
fig.update_layout(
    title={
        'text': 'Métricas de Centralidade da Rede Aérea Brasileira',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'color': '#000000', 'size': 22}
    },
    height=1400,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='#000000'),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Create tabs for different views
tab1, tab2 = st.tabs(["Rankings", "Estatísticas Comparativas"])

with tab1:
    st.markdown("### Rankings Detalhados")
    
    # Show top 10 for each metric side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top 10 - Degree Centrality")
        degree_top = df_centrality.nlargest(10, 'Degree_Centrality')[['IATA', 'Name', 'City', 'Degree_Centrality']]
        st.dataframe(degree_top, use_container_width=True, hide_index=True)
        
        st.markdown("#### Top 10 - Closeness Centrality")
        closeness_top = df_centrality.nlargest(10, 'Closeness_Centrality')[['IATA', 'Name', 'City', 'Closeness_Centrality']]
        st.dataframe(closeness_top, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Top 10 - Betweenness Centrality")
        betweenness_top = df_centrality.nlargest(10, 'Betweenness_Centrality')[['IATA', 'Name', 'City', 'Betweenness_Centrality']]
        st.dataframe(betweenness_top, use_container_width=True, hide_index=True)
        
        st.markdown("#### Top 10 - Eigenvector Centrality")
        eigenvector_top = df_centrality.nlargest(10, 'Eigenvector_Centrality')[['IATA', 'Name', 'City', 'Eigenvector_Centrality']]
        st.dataframe(eigenvector_top, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Estatísticas Comparativas")
    
    # Statistics for all metrics
    for metric, title in centrality_metrics:
        st.markdown(f"#### {title}")
        col1, col2, col3, col4 = st.columns(4)
        
        centrality_vals = df_centrality[metric]
        top_airport = df_centrality.loc[centrality_vals.idxmax()]
        
        with col1:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #ddd; padding: 0.5rem; border-radius: 0.5rem; text-align: center;">
                <div style="color: #666; font-size: 12px; margin-bottom: 0.25rem;">Máximo</div>
                <div style="color: black; font-size: 18px; font-weight: 600;">{centrality_vals.max():.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #ddd; padding: 0.5rem; border-radius: 0.5rem; text-align: center;">
                <div style="color: #666; font-size: 12px; margin-bottom: 0.25rem;">Média</div>
                <div style="color: black; font-size: 18px; font-weight: 600;">{centrality_vals.mean():.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #ddd; padding: 0.5rem; border-radius: 0.5rem; text-align: center;">
                <div style="color: #666; font-size: 12px; margin-bottom: 0.25rem;">Desvio Padrão</div>
                <div style="color: black; font-size: 18px; font-weight: 600;">{centrality_vals.std():.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #ddd; padding: 0.5rem; border-radius: 0.5rem; text-align: center;">
                <div style="color: #666; font-size: 12px; margin-bottom: 0.25rem;">Mais Central</div>
                <div style="color: black; font-size: 18px; font-weight: 600;">{top_airport['IATA']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
