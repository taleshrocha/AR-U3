import matplotlib.pyplot as plt
import networkx as nx
import community as community_louvain
import matplotlib.cm as cm

G_br = st.session_state.G_br

G_undirected = G_br.to_undirected()
partition = community_louvain.best_partition(G_undirected)
colors = [partition[n] for n in G_undirected.nodes()]

fig, ax = plt.subplots(figsize=(10, 8))
nx.draw_networkx(G_undirected, pos=nx.spring_layout(G_undirected, seed=42), 
                 node_color=colors, cmap=cm.get_cmap('tab10'), 
                 with_labels=False, node_size=100, ax=ax)
ax.set_title("Comunidades (Louvain) na Rede de Aeroportos do Brasil")
st.pyplot(fig)
