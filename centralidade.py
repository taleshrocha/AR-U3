import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import seaborn as sns

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br

st.markdown("## 🎯 Análise Avançada de Centralidade")

# Calculate multiple centrality measures
st.info("Calculando métricas de centralidade... Isso pode levar alguns momentos.")

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
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    centrality_metric = st.selectbox(
        "Métrica de Centralidade:",
        ["Degree_Centrality", "Betweenness_Centrality", "Closeness_Centrality", "Eigenvector_Centrality"],
        format_func=lambda x: x.replace('_', ' ').title()
    )

with col2:
    visualization_type = st.selectbox(
        "Tipo de Visualização:",
        ["Scatter Plot", "Network Graph", "Ranking Bars", "Correlation Matrix"]
    )

with col3:
    top_n_display = st.slider("Top N para destacar", 5, 20, 10)

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Visualização Principal", "🔄 Comparação de Métricas", "📈 Rankings"])

with tab1:
    if visualization_type == "Scatter Plot":
        # Enhanced scatter plot
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(
            df_centrality['Degree_Centrality'],
            df_centrality[centrality_metric],
            c=df_centrality[centrality_metric],
            s=df_centrality[centrality_metric]*1000,
            cmap='viridis',
            alpha=0.7
        )
        ax.set_xlabel("Degree Centrality")
        ax.set_ylabel(centrality_metric.replace('_', ' ').title())
        ax.set_title(f"Centralidade: {centrality_metric.replace('_', ' ').title()}")
        plt.colorbar(scatter)
        st.pyplot(fig)
    
    elif visualization_type == "Ranking Bars":
        # Top airports bar chart
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        top_airports.plot(x='IATA', y=centrality_metric, kind='bar', ax=ax, color='orange')
        ax.set_title(f"Top {top_n_display} - {centrality_metric.replace('_', ' ').title()}")
        ax.set_xlabel("Aeroporto (IATA)")
        ax.set_ylabel(centrality_metric.replace('_', ' ').title())
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    elif visualization_type == "Correlation Matrix":
        # Correlation heatmap
        corr_cols = ['Degree_Centrality', 'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality']
        correlation_matrix = df_centrality[corr_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0, ax=ax)
        ax.set_title("Correlação entre Métricas de Centralidade")
        st.pyplot(fig)

with tab2:
    st.markdown("### 🔄 Comparação de Métricas")
    
    # Multi-metric comparison
    metrics_to_compare = st.multiselect(
        "Selecione métricas para comparar:",
        ['Degree_Centrality', 'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality'],
        default=['Degree_Centrality', 'Betweenness_Centrality']
    )
    
    if len(metrics_to_compare) >= 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        df_centrality[metrics_to_compare].boxplot(ax=ax)
        ax.set_title("Distribuição das Métricas de Centralidade")
        ax.set_ylabel("Valor da Centralidade")
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab3:
    st.markdown("### 📈 Rankings Detalhados")
    
    ranking_metric = st.selectbox(
        "Métrica para ranking:",
        ['Degree_Centrality', 'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality'],
        key="ranking_metric"
    )
    
    ranked_df = df_centrality.sort_values(ranking_metric, ascending=False).head(20)
    
    st.dataframe(
        ranked_df[['IATA', 'Name', 'City', ranking_metric]],
        use_container_width=True,
        column_config={
            ranking_metric: st.column_config.NumberColumn(
                ranking_metric.replace('_', ' ').title(),
                format="%.4f"
            )
        }
    )
