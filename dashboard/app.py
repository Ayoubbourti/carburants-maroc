import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import glob

# ========== CONFIG ==========
st.set_page_config(
    page_title="Prix Carburants Maroc | Pro Dashboard",
    page_icon="⛽",
    layout="wide",
)

# ========== CSS PRO ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

/* HEADER */
.main-header {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    padding: 2.5rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255,255,255,0.1);
}

.main-header h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* CARDS */
.metric-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    padding: 1.5rem;
    border-radius: 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-5px);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #020617;
}

/* BUTTON */
.stButton button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    color: white;
}

/* TEXT */
h2, h3 {
    color: #e2e8f0 !important;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #94a3b8;
    padding: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown("""
<div class="main-header">
    <h1>⛽ Prix des Carburants au Maroc</h1>
    <p style="color:#cbd5f5;">Dashboard temps réel • Analyse avancée</p>
</div>
""", unsafe_allow_html=True)

# ========== LOAD DATA ==========
@st.cache_data
def load_data():
    files = glob.glob('data/raw/stations_*.csv')
    if not files:
        return pd.DataFrame()
    file = max(files, key=os.path.getctime)
    df = pd.read_csv(file)

    df['gasoil'] = pd.to_numeric(df['gasoil'], errors='coerce')
    df['essence'] = pd.to_numeric(df['essence'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    return df

df = load_data()

if df.empty:
    st.error("No data found")
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("## ⚙️ Filtres")

    villes = sorted(df['ville'].unique())
    ville_filter = st.multiselect("Ville", villes, default=villes[:5])

    enseignes = sorted(df['enseigne'].dropna().unique())
    enseigne_filter = st.multiselect("Enseigne", enseignes, default=enseignes[:3])

# ========== FILTER ==========
if ville_filter:
    df = df[df['ville'].isin(ville_filter)]

if enseigne_filter:
    df = df[df['enseigne'].isin(enseigne_filter)]

# ========== KPI ==========
st.markdown("## 📊 KPIs")

col1, col2, col3, col4 = st.columns(4)

gasoil = df['gasoil'].mean()
essence = df['essence'].mean()

with col1:
    st.markdown(f'<div class="metric-card"><h3>Gasoil</h3><h2>{gasoil:.2f}</h2></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card"><h3>Essence</h3><h2>{essence:.2f}</h2></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-card"><h3>Stations</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="metric-card"><h3>Villes</h3><h2>{df["ville"].nunique()}</h2></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ========== MAP + CHART ==========
col_map, col_chart = st.columns([2,1])

with col_map:
    st.markdown("## 🗺️ Carte")

    df_map = df.dropna(subset=['latitude','longitude','gasoil'])

    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        color="gasoil",
        size=[10]*len(df_map),
        zoom=5
    )

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(l=0,r=0,t=0,b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

with col_chart:
    st.markdown("## 📈 Prix par ville")

    df_ville = df.groupby("ville")["gasoil"].mean().reset_index()

    fig2 = px.bar(df_ville, x="ville", y="gasoil", text_auto=".2f")
    st.plotly_chart(fig2, use_container_width=True)

# ========== TABLE ==========
st.markdown("## 📋 Stations")

st.dataframe(df[['enseigne','ville','gasoil','essence']])

# ========== FOOTER ==========
st.markdown(f"""
<div class="footer">
    <p>Updated: {datetime.now().strftime('%d/%m/%Y')}</p>
    <p>Made by Ayoub 🚀</p>
</div>
""", unsafe_allow_html=True)