import plotly.graph_objects as go
import networkx as nx

airports_br = st.session_state.airports_br
G_br = st.session_state.G_br

st.markdown("### Selecione dois aeroportos para ver o caminho mais curto")
nomes = airports_br.set_index("Airport ID")["Name"].to_dict()
opcoes = list(nomes.items())
src_id = st.selectbox("Origem", opcoes, index=0, format_func=lambda x: x[1])[0]
dst_id = st.selectbox("Destino", opcoes, index=1, format_func=lambda x: x[1])[0]

try:
    path = nx.shortest_path(G_br, source=src_id, target=dst_id)
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=[airports_br.loc[airports_br["Airport ID"] == i, "Longitude"].values[0] for i in path],
        lat=[airports_br.loc[airports_br["Airport ID"] == i, "Latitude"].values[0] for i in path],
        mode='markers+text',
        marker=dict(size=6, color='red'),
        text=[airports_br.loc[airports_br["Airport ID"] == i, "IATA"].values[0] for i in path],
        textposition="top center"))

    for i in range(len(path) - 1):
        src = airports_br[airports_br["Airport ID"] == path[i]]
        dst = airports_br[airports_br["Airport ID"] == path[i+1]]
        fig.add_trace(go.Scattergeo(
            lon=[src.iloc[0]["Longitude"], dst.iloc[0]["Longitude"]],
            lat=[src.iloc[0]["Latitude"], dst.iloc[0]["Latitude"]],
            mode='lines',
            line=dict(width=2, color='red'),
            showlegend=False))

    fig.update_layout(title='Caminho mais curto', geo_scope='south america', height=500)
    st.plotly_chart(fig)

except nx.NetworkXNoPath:
    st.error("Não existe caminho entre os aeroportos selecionados.")
