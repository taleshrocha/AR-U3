import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import seaborn as sns

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
            'Degree_Centrality': degree_cent[node_id],
            'Betweenness_Centrality': betweenness_cent[node_id],
            'Closeness_Centrality': closeness_cent[node_id],
            'Eigenvector_Centrality': eigenvector_cent[node_id]
        })

df_centrality = pd.DataFrame(centrality_data)

# Interactive controls
col1, col2 = st.columns([1, 1])

with col1:
    centrality_metric = st.selectbox(
        "Métrica de Centralidade:",
        ["Degree_Centrality", "Betweenness_Centrality", "Closeness_Centrality", "Eigenvector_Centrality"],
        format_func=lambda x: x.replace('_', ' ').title()
    )

with col2:
    visualization_type = st.selectbox(
        "Tipo de Visualização:",
        ["Network Graph", "Ranking Bars"]
    )

# Create tabs for different views
tab1, tab2 = st.tabs(["Visualização Principal", "Rankings"])

with tab1:
    top_n_display = st.slider("Top N para destacar", 5, 20, 10)
    
    if visualization_type == "Network Graph":
        # Network graph com cores baseadas na centralidade
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Criar subgrafo com apenas os top aeroportos para melhor visualização
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        top_nodes = top_airports['Airport_ID'].tolist()
        
        # Incluir também conexões entre esses nós
        subgraph_nodes = set(top_nodes)
        for node in top_nodes:
            subgraph_nodes.update(G_br.neighbors(node))
        
        G_sub = G_br.subgraph(list(subgraph_nodes))
        
        # Layout e cores
        pos = nx.spring_layout(G_sub, k=1, iterations=50)
        node_colors = [df_centrality[df_centrality['Airport_ID'] == node][centrality_metric].iloc[0] 
                      if node in df_centrality['Airport_ID'].values else 0 
                      for node in G_sub.nodes()]
        
        node_sizes = [df_centrality[df_centrality['Airport_ID'] == node][centrality_metric].iloc[0] * 2000 + 50
                     if node in df_centrality['Airport_ID'].values else 50
                     for node in G_sub.nodes()]
        
        # Desenhar o grafo
        nx.draw_networkx_nodes(G_sub, pos, node_color=node_colors, node_size=node_sizes, 
                              cmap='viridis', alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G_sub, pos, alpha=0.3, width=0.5, ax=ax)
        
        # Labels apenas para top aeroportos
        top_labels = {}
        for node in top_nodes:
            airport_info = df_centrality[df_centrality['Airport_ID'] == node]
            if not airport_info.empty:
                top_labels[node] = airport_info.iloc[0]['IATA']
        
        nx.draw_networkx_labels(G_sub, pos, labels=top_labels, font_size=8, ax=ax)
        
        ax.set_title(f"Rede de Aeroportos - Colorido por {centrality_metric.replace('_', ' ').title()}")
        ax.axis('off')
        
        # Colorbar
        sm = plt.cm.ScalarMappable(cmap='viridis', 
                                  norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
        sm.set_array([])
        plt.colorbar(sm, ax=ax, label=centrality_metric.replace('_', ' ').title())
        
        st.pyplot(fig)

    elif visualization_type == "Ranking Bars":
        # Top airports bar chart
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        
        fig, ax = plt.subplots(figsize=(6, 4))
        
        top_airports.plot(x='IATA', y=centrality_metric, kind='bar', ax=ax, color='orange')
        ax.set_title(f"Top {top_n_display} - {centrality_metric.replace('_', ' ').title()}")
        ax.set_xlabel("Aeroporto (IATA)")
        ax.set_ylabel(centrality_metric.replace('_', ' ').title())
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab2:
    st.markdown("### Rankings Detalhados")
    
    ranked_df = df_centrality.sort_values(centrality_metric, ascending=False).head(20)
    
    st.dataframe(
        ranked_df[['Name', 'Degree_Centrality', 'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality']],
        use_container_width=True,
        column_config={
            'Name': st.column_config.TextColumn('Aeroporto'),
            'Degree_Centrality': st.column_config.NumberColumn('Degree', format="%.4f"),
            'Betweenness_Centrality': st.column_config.NumberColumn('Betweenness', format="%.4f"),
            'Closeness_Centrality': st.column_config.NumberColumn('Closeness', format="%.4f"),
            'Eigenvector_Centrality': st.column_config.NumberColumn('Eigenvector', format="%.4f")
        }
    )
