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
        fig, ax = plt.subplots(figsize=(12, 10), facecolor='white')  # Larger figure
        ax.set_facecolor('white')
        
        # Criar subgrafo com apenas os top aeroportos para melhor visualização
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        top_nodes = top_airports['Airport_ID'].tolist()
        
        # Incluir também conexões entre esses nós
        subgraph_nodes = set(top_nodes)
        for node in top_nodes:
            subgraph_nodes.update(G_br.neighbors(node))
        
        G_sub = G_br.subgraph(list(subgraph_nodes))
        
        # Layout e cores com melhor espaçamento
        pos = nx.spring_layout(G_sub, k=4, iterations=150, seed=42)  # Increased spacing
        node_colors = [df_centrality[df_centrality['Airport_ID'] == node][centrality_metric].iloc[0] 
                      if node in df_centrality['Airport_ID'].values else 0 
                      for node in G_sub.nodes()]
        
        node_sizes = [df_centrality[df_centrality['Airport_ID'] == node][centrality_metric].iloc[0] * 3000 + 100
                     if node in df_centrality['Airport_ID'].values else 100
                     for node in G_sub.nodes()]  # Larger nodes for better visibility
        
        # Desenhar o grafo com edges mais finas
        nx.draw_networkx_nodes(G_sub, pos, node_color=node_colors, node_size=node_sizes, 
                              cmap='Blues', alpha=0.9, linewidths=1.5, edgecolors='#000000', ax=ax)  # Thinner borders
        nx.draw_networkx_edges(G_sub, pos, alpha=0.3, width=0.5, edge_color='#333333', ax=ax)  # Much thinner edges
        
        # Labels apenas para top aeroportos
        top_labels = {}
        for node in top_nodes:
            airport_info = df_centrality[df_centrality['Airport_ID'] == node]
            if not airport_info.empty:
                top_labels[node] = airport_info.iloc[0]['IATA']
        
        nx.draw_networkx_labels(G_sub, pos, labels=top_labels, font_size=9, font_color='#000000', 
                               font_weight='bold', ax=ax)
        
        ax.set_title(f"Rede de Aeroportos - Colorido por {centrality_metric.replace('_', ' ').title()}", 
                    color='#000000', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # Colorbar
        sm = plt.cm.ScalarMappable(cmap='Blues', 
                                  norm=plt.Normalize(vmin=min(node_colors), vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label=centrality_metric.replace('_', ' ').title())
        cbar.ax.tick_params(labelsize=10, colors='#000000')
        cbar.set_label(centrality_metric.replace('_', ' ').title(), fontsize=12, color='#000000', fontweight='bold')
        
        st.pyplot(fig)

    elif visualization_type == "Ranking Bars":
        # Top airports bar chart
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
        ax.set_facecolor('white')
        
        bars = ax.bar(top_airports['IATA'], top_airports[centrality_metric], color='#1E90FF', 
                     edgecolor='#000000', linewidth=1)
        ax.set_title(f"Top {top_n_display} - {centrality_metric.replace('_', ' ').title()}", 
                    color='#000000', fontsize=16, fontweight='bold')
        ax.set_xlabel("Aeroporto (IATA)", color='#000000', fontsize=12, fontweight='bold')
        ax.set_ylabel(centrality_metric.replace('_', ' ').title(), color='#000000', fontsize=12, fontweight='bold')
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#000000')
        
        for spine in ax.spines.values():
            spine.set_color('#000000')
            spine.set_linewidth(2)
        plt.xticks(rotation=45)
        plt.tight_layout()
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
