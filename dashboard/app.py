import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import glob

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="Prix Carburants Maroc | Dashboard Pro",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS PERSONNALISÉ (Design Pro) ==========
st.markdown("""
<style>
    /* Police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #fff 0%, #a8c0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        color: #a8c0ff;
        margin-top: 0.5rem;
    }
    
    /* Cartes métriques */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar stylisée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e0e0e0;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown("""
<div class="main-header">
    <h1>⛽ Prix des Carburants au Maroc</h1>
    <p>Analyse en temps réel des prix du gasoil et de l'essence • 349 stations • 16 villes</p>
</div>
""", unsafe_allow_html=True)

# ========== CHARGEMENT DES DONNÉES ==========
@st.cache_data(ttl=3600)
def load_data():
    csv_files = glob.glob('data/raw/stations_*.csv')
    if not csv_files:
        return pd.DataFrame()
    latest_file = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    df['gasoil'] = pd.to_numeric(df['gasoil'], errors='coerce')
    df['essence'] = pd.to_numeric(df['essence'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    return df

df = load_data()

if df.empty:
    st.error("❌ Aucune donnée. Lance `python src/extract.py`")
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("## ⛽ Menu")
    st.markdown("---")
    
    # Filtres
    st.markdown("### 🔍 Filtres")
    villes = sorted(df['ville'].unique())
    ville_filter = st.multiselect("Villes", villes, default=villes[:5])
    
    enseignes = sorted(df['enseigne'].dropna().unique())
    enseigne_filter = st.multiselect("Enseignes", enseignes, default=enseignes[:3])
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Statistiques")
    st.metric("Total stations", len(df))
    st.metric("Avec prix gasoil", df['gasoil'].notna().sum())
    st.metric("Avec prix essence", df['essence'].notna().sum())
    
    st.markdown("---")
    
    # Info
    st.markdown("### ℹ️ À propos")
    st.caption(f"Dernière mise à jour")
    st.caption(f"{datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    st.caption("Made with ❤️ by **Ayoub Bourti**")

# ========== FILTRAGE ==========
if ville_filter:
    df = df[df['ville'].isin(ville_filter)]
if enseigne_filter:
    df = df[df['enseigne'].isin(enseigne_filter)]

# ========== KPI CARDS ==========
st.markdown("## 📈 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

prix_gasoil = df[df['gasoil'].notna()]['gasoil'].mean()
prix_essence = df[df['essence'].notna()]['essence'].mean()
stations_prix = df['gasoil'].notna().sum()
villes_count = df['ville'].nunique()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>⛽ Gasoil</h3>
        <h2>{prix_gasoil:.2f} DH/L</h2>
        <small>Prix moyen</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h3>⛽ Essence</h3>
        <h2>{prix_essence:.2f} DH/L</h2>
        <small>Prix moyen</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h3>🏪 Stations</h3>
        <h2>{stations_prix}</h2>
        <small>Avec prix disponibles</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <h3>🏙️ Villes</h3>
        <h2>{villes_count}</h2>
        <small>Couvertes</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== DEUX COLONNES PRINCIPALES ==========
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.markdown("## 🗺️ Carte interactive")
    stations_carte = df[df['latitude'].notna() & df['longitude'].notna() & df['gasoil'].notna()]
    
    if not stations_carte.empty:
        fig_map = px.scatter_mapbox(
            stations_carte,
            lat='latitude',
            lon='longitude',
            color='gasoil',
            size=[10] * len(stations_carte),
            hover_name='nom',
            hover_data={'enseigne': True, 'ville': True, 'gasoil': ':.2f'},
            color_continuous_scale='RdYlGn_r',
            zoom=6,
            height=500
        )
        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0, "t":0, "l":0, "b":0},
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Aucune station avec coordonnées disponibles")

with col_chart:
    st.markdown("## 📊 Prix par ville")
    prix_ville = df[df['gasoil'].notna()].groupby('ville')['gasoil'].mean().sort_values().reset_index()
    
    if not prix_ville.empty:
        fig_bar = px.bar(
            prix_ville,
            x='ville',
            y='gasoil',
            color='gasoil',
            color_continuous_scale='RdYlGn_r',
            title="Prix moyen du Gasoil",
            labels={'gasoil': 'DH/L', 'ville': ''},
            text_auto='.2f'
        )
        fig_bar.update_layout(
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ========== TOP STATIONS ==========
st.markdown("## 🏆 Top 10 stations les moins chères")

tab1, tab2 = st.tabs(["🟢 Gasoil", "🔵 Essence"])

with tab1:
    top_gasoil = df[df['gasoil'].notna()].nsmallest(10, 'gasoil')[['enseigne', 'ville', 'gasoil', 'adresse']]
    top_gasoil.columns = ['Enseigne', 'Ville', 'Prix (DH/L)', 'Adresse']
    st.dataframe(top_gasoil, use_container_width=True)

with tab2:
    top_essence = df[df['essence'].notna()].nsmallest(10, 'essence')[['enseigne', 'ville', 'essence', 'adresse']]
    top_essence.columns = ['Enseigne', 'Ville', 'Prix (DH/L)', 'Adresse']
    st.dataframe(top_essence, use_container_width=True)

# ========== CALCULATEUR ==========
st.markdown("---")
st.markdown("## 💰 Calculateur d'économies")

with st.container():
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        litres = st.slider("📏 Litres par plein", 20, 80, 50, format="%d L")
        ville_calc = st.selectbox("📍 Ville", options=sorted(df[df['gasoil'].notna()]['ville'].unique()))
    
    with col_calc2:
        stations_ville = df[(df['ville'] == ville_calc) & (df['gasoil'].notna())]
        if not stations_ville.empty:
            prix_min = stations_ville['gasoil'].min()
            prix_max = stations_ville['gasoil'].max()
            econo_plein = (prix_max - prix_min) * litres
            
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); margin-top: 0;">
                <h3>💰 Économie par plein</h3>
                <h2>{econo_plein:.0f} DH</h2>
                <small>En choisissant la station la moins chère de {ville_calc}</small>
                <hr>
                <small>📅 Mensuel (4 pleins): <b>{econo_plein * 4:.0f} DH</b></small>
                <br>
                <small>📅 Annuel (48 pleins): <b>{econo_plein * 48:.0f} DH</b></small>
            </div>
            """, unsafe_allow_html=True)

# ========== TABLEAU COMPLET ==========
with st.expander("📋 Liste complète des stations"):
    display_df = df[['enseigne', 'ville', 'gasoil', 'essence', 'adresse']].copy()
    display_df.columns = ['Enseigne', 'Ville', 'Gasoil (DH/L)', 'Essence (DH/L)', 'Adresse']
    st.dataframe(display_df, use_container_width=True)

# ========== FOOTER ==========
st.markdown("""
<div class="footer">
    <p>📊 Données mises à jour automatiquement 2x par jour via GitHub Actions</p>
    <p>🔗 <a href="https://github.com/Ayoubbourti/carburants-maroc" target="_blank">GitHub</a> • 
       <a href="https://carburants-maroc.streamlit.app" target="_blank">Dashboard</a> • 
       Made with ❤️ by <strong>Ayoub Bourti</strong></p>
</div>
""", unsafe_allow_html=True)