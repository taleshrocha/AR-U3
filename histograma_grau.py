import matplotlib.pyplot as plt
import seaborn as sns

G_br = st.session_state.G_br

graus = [d for n, d in G_br.degree()]
fig, ax = plt.subplots()
sns.histplot(graus, bins=30, kde=True, ax=ax)
ax.set_title("Distribuição de Grau dos Aeroportos (Brasil)")
ax.set_xlabel("Grau")
ax.set_ylabel("Frequência")
st.pyplot(fig)
