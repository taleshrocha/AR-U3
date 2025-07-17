import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

G_br = st.session_state.G_br

adj = nx.to_numpy_array(G_br)
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(adj, cmap="Blues", cbar=False, ax=ax)
ax.set_title("Matriz de Adjacência - Aeroportos do Brasil")
st.pyplot(fig)
