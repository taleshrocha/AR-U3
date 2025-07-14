import plotly.graph_objects as go

airports_br = st.session_state.airports_br
routes_br = st.session_state.routes_br

fig = go.Figure()
fig.add_trace(go.Scattergeo(
    lon=airports_br['Longitude'],
    lat=airports_br['Latitude'],
    text=airports_br['Name'],
    mode='markers',
    marker=dict(size=5, color='blue'),
    name='Aeroportos'))

for _, row in routes_br.iterrows():
    src = airports_br[airports_br['Airport ID'] == row['Source airport ID']]
    dst = airports_br[airports_br['Airport ID'] == row['Destination airport ID']]
    if not src.empty and not dst.empty:
        fig.add_trace(go.Scattergeo(
            lon=[src.iloc[0]['Longitude'], dst.iloc[0]['Longitude']],
            lat=[src.iloc[0]['Latitude'], dst.iloc[0]['Latitude']],
            mode='lines',
            line=dict(width=1, color='gray'),
            opacity=0.3,
            showlegend=False))

fig.update_layout(
    title='Rotas Aéreas no Brasil',
    geo_scope='south america',
    height=600)

st.plotly_chart(fig)
