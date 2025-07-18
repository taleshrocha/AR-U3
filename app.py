import streamlit as st
import pandas as pd
import networkx as nx

st.set_page_config(
    layout="wide",
    page_title="Análise da Rede Aérea Brasileira",
)

st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f0f0f0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #000000;
        background-color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #000000;
        border-color: #000000;
        font-weight: bold;
    }
    .stSelectbox label {
        color: #000000 !important;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stSlider label {
        color: #000000 !important;
        font-weight: bold;
    }
    .stCheckbox label {
        color: #000000 !important;
        font-weight: bold;
    }
    .stButton button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: bold !important;
    }
    .stButton button:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .stButton button:focus {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .stMetric label {
        color: #000000 !important;
        font-weight: bold;
    }
    .stMetric [data-testid="metric-value"] {
        color: #000000 !important;
        font-weight: bold;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    .stMarkdown {
        color: #000000;
    }
    .stExpander label {
        color: #000000 !important;
        font-weight: bold;
    }
    .stExpander > div {
        background-color: #ffffff !important;
    }
    /* Enhanced dataframe styling */
    .stDataFrame {
        background-color: #ffffff !important;
    }
    .stDataFrame table {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stDataFrame thead th {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stDataFrame tbody td {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    div[data-testid="stDataFrame"] table {
        background-color: #ffffff !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    div[data-testid="stDataFrame"] td {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    /* Additional dataframe selectors */
    [data-testid="stDataFrame"] div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    .stDataFrame > div {
        background-color: #ffffff !important;
    }
    .css-1kyxreq {
        background-color: #ffffff !important;
    }
    .streamlit-expanderContent .stDataFrame {
        background-color: #ffffff !important;
    }
    .element-container .stSelectbox > div {
        background-color: #ffffff !important;
    }
    .stSelectbox select {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Análise Rede Aérea Brasileira")

@st.cache_data
def load_data():
    airports = pd.read_csv("airports.dat", header=None)
    routes = pd.read_csv("routes.dat", header=None)
    airports.columns = ["Airport ID","Name","City","Country","IATA","ICAO","Latitude","Longitude","Altitude","Timezone","DST","Database Timezone","Type","Source"]
    routes.columns = ["Airline","Airline ID","Source airport","Source airport ID","Destination airport","Destination airport ID","Codeshare","Stops","Equipment"]
    return airports, routes

airports, routes = load_data()

airports_br = airports[airports['Country'] == 'Brazil'].copy()
airport_ids_br = set(airports_br["Airport ID"])

# Check data types and clean the data
routes = routes.dropna(subset=["Source airport ID", "Destination airport ID"])
routes["Source airport ID"] = pd.to_numeric(routes["Source airport ID"], errors='coerce')
routes["Destination airport ID"] = pd.to_numeric(routes["Destination airport ID"], errors='coerce')
routes = routes.dropna(subset=["Source airport ID", "Destination airport ID"])

# Convert to int after cleaning
routes["Source airport ID"] = routes["Source airport ID"].astype(int)
routes["Destination airport ID"] = routes["Destination airport ID"].astype(int)

routes_br = routes[routes["Source airport ID"].isin(airport_ids_br) &
                   routes["Destination airport ID"].isin(airport_ids_br)].copy()

G_br = nx.DiGraph()

for _, row in airports_br.iterrows():
    G_br.add_node(int(row["Airport ID"]), **row.to_dict())

for _, row in routes_br.iterrows():
    G_br.add_edge(int(row["Source airport ID"]), int(row["Destination airport ID"]))

st.session_state.airports_br = airports_br
st.session_state.routes_br = routes_br
st.session_state.G_br = G_br

# Enhanced page selection with descriptions
page_options = {
    "Mapa de Rotas Interativo",
    "Dashboard de Grau", 
    "Centralidade",
    "Caminho Mais Curto",
    "Comunidades e Clusters"
}

page = st.selectbox(
    "Selecione a visualização:",
    page_options,
    format_func=lambda x: f"{x}"
)

if page == "Mapa de Rotas Interativo":
    exec(open("mapa_rotas.py").read())
elif page == "Dashboard de Grau":
    exec(open("histograma_grau.py").read())
elif page == "Centralidade":
    exec(open("centralidade.py").read())
elif page == "Caminho Mais Curto":
    exec(open("caminho_curto.py").read())
elif page == "Comunidades e Clusters":
    exec(open("comunidades.py").read())
