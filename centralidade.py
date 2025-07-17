import matplotlib.pyplot as plt
import networkx as nx
import panel as pn
import holoviews as hv
from holoviews import opts
import pandas as pd
import numpy as np

# Check compatibility
try:
    import bokeh
    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

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
        # Enhanced scatter plot with size and color mapping
        try:
            scatter_plot = df_centrality.hvplot.scatter(
                x='Degree_Centrality',
                y=centrality_metric,
                size=centrality_metric,
                color=centrality_metric,
                hover_cols=['IATA', 'Name', 'City'],
                title=f"Centralidade: {centrality_metric.replace('_', ' ').title()}",
                xlabel="Degree Centrality",
                ylabel=centrality_metric.replace('_', ' ').title(),
                width=700,
                height=500,
                colormap='viridis',
                size_index=1000
            )
            
            if BOKEH_AVAILABLE:
                bokeh_scatter = hv.render(scatter_plot, backend='bokeh')
                st.bokeh_chart(bokeh_scatter, use_container_width=True)
            else:
                # Fallback to matplotlib
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
                
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
            # Simple fallback
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.scatter(df_centrality['Degree_Centrality'], df_centrality[centrality_metric])
            ax.set_xlabel("Degree Centrality")
            ax.set_ylabel(centrality_metric.replace('_', ' ').title())
            st.pyplot(fig)
    
    elif visualization_type == "Network Graph":
        # Network visualization with centrality-based node sizes
        pos = nx.spring_layout(G_br, k=1, iterations=50, seed=42)
        
        # Create network data for plotting
        edge_data = []
        for edge in G_br.edges():
            src_pos = pos[edge[0]]
            dst_pos = pos[edge[1]]
            edge_data.append({
                'x0': src_pos[0], 'y0': src_pos[1],
                'x1': dst_pos[0], 'y1': dst_pos[1]
            })
        
        node_data = []
        for node_id in G_br.nodes():
            node_pos = pos[node_id]
            airport_info = airports_br[airports_br['Airport ID'] == node_id]
            if not airport_info.empty:
                node_data.append({
                    'x': node_pos[0],
                    'y': node_pos[1],
                    'size': df_centrality[df_centrality['Airport_ID'] == node_id][centrality_metric].iloc[0] * 1000,
                    'IATA': airport_info.iloc[0]['IATA'],
                    'centrality': df_centrality[df_centrality['Airport_ID'] == node_id][centrality_metric].iloc[0]
                })
        
        df_nodes = pd.DataFrame(node_data)
        
        # Create network plot
        network_plot = df_nodes.hvplot.scatter(
            x='x', y='y',
            size='size',
            color='centrality',
            hover_cols=['IATA'],
            title=f"Rede Aérea - Tamanho por {centrality_metric.replace('_', ' ').title()}",
            width=700,
            height=500,
            colormap='plasma'
        )
        
        bokeh_network = hv.render(network_plot, backend='bokeh')
        st.bokeh_chart(bokeh_network, use_container_width=True)
    
    elif visualization_type == "Ranking Bars":
        # Top airports bar chart
        top_airports = df_centrality.nlargest(top_n_display, centrality_metric)
        
        try:
            bar_plot = top_airports.hvplot.bar(
                x='IATA',
                y=centrality_metric,
                title=f"Top {top_n_display} - {centrality_metric.replace('_', ' ').title()}",
                xlabel="Aeroporto (IATA)",
                ylabel=centrality_metric.replace('_', ' ').title(),
                color='orange',
                width=700,
                height=400,
                rot=45
            )
            
            if BOKEH_AVAILABLE:
                bokeh_bar = hv.render(bar_plot, backend='bokeh')
                st.bokeh_chart(bokeh_bar, use_container_width=True)
            else:
                # Fallback to matplotlib
                fig, ax = plt.subplots(figsize=(10, 6))
                top_airports.plot(x='IATA', y=centrality_metric, kind='bar', ax=ax, color='orange')
                ax.set_title(f"Top {top_n_display} - {centrality_metric.replace('_', ' ').title()}")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
            # Simple fallback
            fig, ax = plt.subplots(figsize=(10, 6))
            top_airports.plot(x='IATA', y=centrality_metric, kind='bar', ax=ax, color='orange')
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    elif visualization_type == "Correlation Matrix":
        # Correlation heatmap
        corr_cols = ['Degree_Centrality', 'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality']
        correlation_matrix = df_centrality[corr_cols].corr()
        
        try:
            heatmap_plot = correlation_matrix.hvplot.heatmap(
                title="Correlação entre Métricas de Centralidade",
                width=500,
                height=400,
                colormap='RdBu_r',
                clim=(-1, 1)
            )
            
            if BOKEH_AVAILABLE:
                bokeh_heatmap = hv.render(heatmap_plot, backend='bokeh')
                st.bokeh_chart(bokeh_heatmap, use_container_width=True)
            else:
                # Fallback to seaborn
                fig, ax = plt.subplots(figsize=(8, 6))
                import seaborn as sns
                sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0, ax=ax)
                ax.set_title("Correlação entre Métricas de Centralidade")
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
            # Simple fallback
            fig, ax = plt.subplots(figsize=(8, 6))
            import seaborn as sns
            sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', ax=ax)
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
        comparison_df = df_centrality[['IATA'] + metrics_to_compare].melt(
            id_vars=['IATA'], 
            var_name='Metric', 
            value_name='Value'
        )
        
        box_plot = comparison_df.hvplot.box(
            y='Value',
            by='Metric',
            title="Distribuição das Métricas de Centralidade",
            width=600,
            height=400
        )
        
        bokeh_box = hv.render(box_plot, backend='bokeh')
        st.bokeh_chart(bokeh_box, use_container_width=True)

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
