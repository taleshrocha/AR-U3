import matplotlib.pyplot as plt
import networkx as nx

G_br = st.session_state.G_br

centralidade = nx.degree_centrality(G_br)
sizes = [centralidade[n]*1000 for n in G_br.nodes()]
pos = nx.spring_layout(G_br, seed=42)
fig, ax = plt.subplots(figsize=(10, 8))
nx.draw_networkx_nodes(G_br, pos, node_size=sizes, node_color='skyblue', ax=ax)
nx.draw_networkx_edges(G_br, pos, alpha=0.2, ax=ax)
ax.set_title("Centralidade de Grau - Rede Aérea do Brasil")
ax.axis("off")
st.pyplot(fig)
