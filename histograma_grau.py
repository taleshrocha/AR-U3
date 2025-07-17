import matplotlib.pyplot as plt
import seaborn as sns
import panel as pn
import holoviews as hv
from holoviews import opts
import pandas as pd
import numpy as np

# Check if Bokeh backend is available
try:
    import bokeh
    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br

st.markdown("## 📊 Dashboard de Análise de Graus")

# Create degree analysis dataframe
degrees_data = []
for node_id, degree in G_br.degree():
    airport_info = airports_br[airports_br['Airport ID'] == node_id]
    if not airport_info.empty:
        degrees_data.append({
            'Airport_ID': node_id,
            'IATA': airport_info.iloc[0]['IATA'],
            'Name': airport_info.iloc[0]['Name'],
            'City': airport_info.iloc[0]['City'],
            'Degree': degree
        })

df_degrees = pd.DataFrame(degrees_data)

# Interactive controls
col1, col2 = st.columns([1, 1])

with col1:
    bins_count = st.slider("Número de Bins", 10, 50, 25)
    show_kde = st.checkbox("Mostrar KDE", value=True)

with col2:
    min_degree = st.slider("Grau Mínimo para Tabela", 0, df_degrees['Degree'].max(), 5)
    top_n = st.slider("Top N Aeroportos", 5, 20, 10)

# Create multiple visualization tabs
tab1, tab2, tab3 = st.tabs(["📈 Distribuição", "🏆 Rankings", "📋 Dados Detalhados"])

with tab1:
    # Enhanced histogram using hvplot with fallback
    st.markdown("### Distribuição de Graus dos Aeroportos")
    
    try:
        # Create histogram with hvplot
        hist_plot = df_degrees.hvplot.hist(
            y='Degree', 
            bins=bins_count,
            title="Distribuição de Graus",
            xlabel="Grau (Número de Conexões)",
            ylabel="Frequência",
            color='skyblue',
            alpha=0.7,
            width=600,
            height=400
        )
        
        if show_kde:
            kde_plot = df_degrees.hvplot.kde(
                y='Degree',
                color='red',
                line_width=2,
                width=600,
                height=400
            )
            combined_plot = hist_plot * kde_plot
        else:
            combined_plot = hist_plot
        
        # Convert to bokeh and display
        if BOKEH_AVAILABLE:
            bokeh_plot = hv.render(combined_plot, backend='bokeh')
            st.bokeh_chart(bokeh_plot, use_container_width=True)
        else:
            # Fallback to matplotlib
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df_degrees['Degree'], bins=bins_count, alpha=0.7, color='skyblue', edgecolor='black')
            if show_kde:
                sns.kdeplot(data=df_degrees, x='Degree', ax=ax, color='red', linewidth=2)
            ax.set_xlabel("Grau (Número de Conexões)")
            ax.set_ylabel("Frequência")
            ax.set_title("Distribuição de Graus")
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"Erro na visualização: {e}")
        # Fallback to matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df_degrees['Degree'], bins=bins_count, alpha=0.7, color='skyblue', edgecolor='black')
        if show_kde:
            sns.kdeplot(data=df_degrees, x='Degree', ax=ax, color='red', linewidth=2)
        ax.set_xlabel("Grau (Número de Conexões)")
        ax.set_ylabel("Frequência")
        ax.set_title("Distribuição de Graus")
        st.pyplot(fig)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Grau Médio", f"{df_degrees['Degree'].mean():.2f}")
    with col2:
        st.metric("Grau Máximo", df_degrees['Degree'].max())
    with col3:
        st.metric("Desvio Padrão", f"{df_degrees['Degree'].std():.2f}")
    with col4:
        st.metric("Mediana", df_degrees['Degree'].median())

with tab2:
    st.markdown("### Rankings de Conectividade")
    
    # Top connected airports
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥇 Aeroportos Mais Conectados")
        top_airports = df_degrees.nlargest(top_n, 'Degree')[['IATA', 'Name', 'City', 'Degree']]
        
        try:
            # Create bar chart
            bar_plot = top_airports.hvplot.bar(
                x='IATA', 
                y='Degree',
                title=f"Top {top_n} Aeroportos por Conectividade",
                xlabel="Código IATA",
                ylabel="Número de Conexões",
                color='green',
                width=400,
                height=300,
                rot=45
            )
            
            if BOKEH_AVAILABLE:
                bokeh_bar = hv.render(bar_plot, backend='bokeh')
                st.bokeh_chart(bokeh_bar, use_container_width=True)
            else:
                # Fallback to matplotlib
                fig, ax = plt.subplots(figsize=(8, 6))
                top_airports.plot(x='IATA', y='Degree', kind='bar', ax=ax, color='green')
                ax.set_title(f"Top {top_n} Aeroportos por Conectividade")
                ax.set_xlabel("Código IATA")
                ax.set_ylabel("Número de Conexões")
                plt.xticks(rotation=45)
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
            # Simple fallback
            fig, ax = plt.subplots(figsize=(8, 6))
            top_airports.plot(x='IATA', y='Degree', kind='bar', ax=ax, color='green')
            ax.set_title(f"Top {top_n} Aeroportos por Conectividade")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        st.dataframe(top_airports, use_container_width=True)
    
    with col2:
        st.markdown("#### 📉 Distribuição por Faixas")
        
        # Create degree ranges
        df_degrees['Faixa'] = pd.cut(
            df_degrees['Degree'], 
            bins=[0, 1, 5, 10, 20, float('inf')],
            labels=['1', '2-5', '6-10', '11-20', '20+']
        )
        
        faixa_counts = df_degrees['Faixa'].value_counts().reset_index()
        faixa_counts.columns = ['Faixa', 'Quantidade']
        
        try:
            # Pie chart using hvplot
            pie_plot = faixa_counts.hvplot.pie(
                y='Quantidade',
                by='Faixa',
                title="Aeroportos por Faixa de Conectividade",
                width=400,
                height=300
            )
            
            if BOKEH_AVAILABLE:
                bokeh_pie = hv.render(pie_plot, backend='bokeh')
                st.bokeh_chart(bokeh_pie, use_container_width=True)
            else:
                # Fallback to matplotlib
                fig, ax = plt.subplots(figsize=(6, 6))
                ax.pie(faixa_counts['Quantidade'], labels=faixa_counts['Faixa'], autopct='%1.1f%%')
                ax.set_title("Aeroportos por Faixa de Conectividade")
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Erro na visualização: {e}")
            # Simple fallback
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(faixa_counts['Quantidade'], labels=faixa_counts['Faixa'], autopct='%1.1f%%')
            ax.set_title("Aeroportos por Faixa de Conectividade")
            st.pyplot(fig)
        
        st.dataframe(faixa_counts, use_container_width=True)

with tab3:
    st.markdown("### 📋 Dados Detalhados dos Aeroportos")
    
    # Filter data
    filtered_df = df_degrees[df_degrees['Degree'] >= min_degree].sort_values('Degree', ascending=False)
    
    # Enhanced table with search and filtering
    st.markdown(f"**{len(filtered_df)}** aeroportos com grau ≥ {min_degree}")
    
    # Add search functionality
    search_term = st.text_input("🔍 Buscar por IATA, Nome ou Cidade:")
    if search_term:
        mask = (
            filtered_df['IATA'].str.contains(search_term, case=False, na=False) |
            filtered_df['Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['City'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Display interactive table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "IATA": st.column_config.TextColumn("Código IATA", width="small"),
            "Name": st.column_config.TextColumn("Nome do Aeroporto", width="large"),
            "City": st.column_config.TextColumn("Cidade", width="medium"),
            "Degree": st.column_config.NumberColumn("Conexões", width="small")
        }
    )
