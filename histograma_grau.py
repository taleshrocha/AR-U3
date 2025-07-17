import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

G_br = st.session_state.G_br
airports_br = st.session_state.airports_br

st.markdown("## Análise de Grau")

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
top_n = st.slider("Top N Aeroportos", 5, 20, 10)

st.markdown("### Distribuição de Graus dos Aeroportos")

# Create histogram
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df_degrees['Degree'], bins=25, alpha=0.7, color='skyblue', edgecolor='black')
ax.set_xlabel("Grau (Número de Conexões)", fontsize=10)
ax.set_ylabel("Frequência", fontsize=10)
ax.set_title("Distribuição de Graus", fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=8)
ax.grid(True, alpha=0.3)
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

st.markdown("### Aeroportos Mais Conectados")
top_airports = df_degrees.nlargest(top_n, 'Degree')[['Name', 'City', 'Degree']]

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    # Create bar chart with airport names
    fig, ax = plt.subplots(figsize=(10, 8))

    # Truncate long names for display
    display_names = [name[:25] + '...' if len(name) > 25 else name for name in top_airports['Name']]

    bars = ax.barh(range(len(top_airports)), top_airports['Degree'], color='green')
    ax.set_yticks(range(len(top_airports)))
    ax.set_yticklabels(display_names, fontsize=8)
    ax.set_xlabel("Número de Conexões", fontsize=10)
    ax.set_title(f"Top {top_n} Aeroportos por Conectividade", fontsize=12)
    ax.tick_params(axis='x', which='major', labelsize=8)

    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
               f'{int(width)}', ha='left', va='center', fontsize=8)

    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("#### Distribuição por Faixas de Grau")
    
    # Create degree ranges
    df_degrees['Faixa'] = pd.cut(
        df_degrees['Degree'], 
        bins=[0, 1, 5, 10, 20, float('inf')],
        labels=['1', '2-5', '6-10', '11-20', '20+']
    )
    
    faixa_counts = df_degrees['Faixa'].value_counts().reset_index()
    faixa_counts.columns = ['Faixa', 'Quantidade']
    
    # Pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(faixa_counts['Quantidade'], labels=faixa_counts['Faixa'], autopct='%1.1f%%')
    ax.set_title("Aeroportos por Faixa de Conectividade", fontsize=12)
    plt.setp(ax.texts, fontsize=8)
    st.pyplot(fig)
