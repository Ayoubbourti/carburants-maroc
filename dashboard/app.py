import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import glob

st.set_page_config(
    page_title="Prix Carburants Maroc",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Prix des Carburants au Maroc")
st.caption(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ========== CHARGEMENT DES DONNÉES ==========
@st.cache_data
def load_data():
    """Charge les données depuis le dossier data/raw/"""
    
    # Cherche tous les fichiers CSV dans data/raw/
    csv_files = glob.glob('data/raw/stations_*.csv')
    
    if not csv_files:
        return pd.DataFrame()
    
    # Prend le fichier le plus récent
    latest_file = max(csv_files, key=os.path.getctime)
    
    df = pd.read_csv(latest_file)
    
    # Convertit les prix en nombres
    df['gasoil'] = pd.to_numeric(df['gasoil'], errors='coerce')
    df['essence'] = pd.to_numeric(df['essence'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    return df

df = load_data()

if df.empty:
    st.error("❌ Aucune donnée trouvée! Lance `python src/extract.py` d'abord")
    st.stop()

# ========== SIDEBAR ==========
st.sidebar.header("📊 Informations")
st.sidebar.write(f"**Stations totales:** {len(df)}")
st.sidebar.write(f"**Avec prix gasoil:** {df['gasoil'].notna().sum()}")
st.sidebar.write(f"**Avec prix essence:** {df['essence'].notna().sum()}")
st.sidebar.write(f"**Villes:** {df['ville'].nunique()}")

# Filtre par ville
villes = sorted(df['ville'].unique())
ville_filter = st.sidebar.multiselect("Filtrer par ville", villes, default=villes[:5] if len(villes) > 5 else villes)

if ville_filter:
    df = df[df['ville'].isin(ville_filter)]

# ========== KPI CARDS ==========
col1, col2, col3, col4 = st.columns(4)

prix_gasoil = df[df['gasoil'].notna()]['gasoil'].mean()
prix_essence = df[df['essence'].notna()]['essence'].mean()
stations_avec_prix = df['gasoil'].notna().sum()

with col1:
    if pd.notna(prix_gasoil):
        st.metric("⛽ Prix moyen Gasoil", f"{prix_gasoil:.2f} DH/L")
    else:
        st.metric("⛽ Prix moyen Gasoil", "N/A")

with col2:
    if pd.notna(prix_essence):
        st.metric("⛽ Prix moyen Essence", f"{prix_essence:.2f} DH/L")
    else:
        st.metric("⛽ Prix moyen Essence", "N/A")

with col3:
    st.metric("🏪 Stations avec prix", stations_avec_prix)

with col4:
    st.metric("🏙️ Villes", df['ville'].nunique())

# ========== CARTE INTERACTIVE ==========
st.subheader("🗺️ Stations-service - Carte interactive")

stations_carte = df[df['latitude'].notna() & df['longitude'].notna() & df['gasoil'].notna()].copy()

if not stations_carte.empty:
    fig_map = px.scatter_mapbox(
        stations_carte,
        lat='latitude',
        lon='longitude',
        color='gasoil',
        size=[8] * len(stations_carte),
        hover_name='nom',
        hover_data={'enseigne': True, 'ville': True, 'gasoil': ':.2f', 'adresse': True},
        color_continuous_scale='RdYlGn_r',
        title="Prix du Gasoil (vert = moins cher)",
        zoom=6,
        height=500
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0, "t":30, "l":0, "b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Aucune station avec coordonnées et prix disponible")

# ========== GRAPHIQUE PAR VILLE ==========
st.subheader("📊 Prix moyen du Gasoil par ville")

prix_ville = df[df['gasoil'].notna()].groupby('ville').agg({
    'gasoil': ['mean', 'min', 'max', 'count']
}).round(2)

if not prix_ville.empty:
    prix_ville.columns = ['Prix moyen', 'Prix min', 'Prix max', 'Nb stations']
    prix_ville = prix_ville.sort_values('Prix moyen')
    
    fig = px.bar(
        prix_ville.reset_index(),
        x='ville',
        y='Prix moyen',
        color='Prix moyen',
        color_continuous_scale='RdYlGn_r',
        title="Prix moyen du Gasoil par ville",
        labels={'Prix moyen': 'DH/L', 'ville': ''}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des prix par ville
    st.subheader("📋 Détail des prix par ville")
    st.dataframe(prix_ville, use_container_width=True)
# ========== GRAPHIQUE HISTORIQUE ==========
st.subheader("📈 Évolution des prix dans le temps")

# Charge l'historique complet
hist_file = "data/processed/historique.csv"
if os.path.exists(hist_file):
    historique = pd.read_csv(hist_file)
    historique['date_extraction'] = pd.to_datetime(historique['date_extraction'])
    
    # Sélection des villes
    villes_histo = st.multiselect(
        "Sélectionne les villes à comparer",
        options=sorted(historique['ville'].unique()),
        default=['Casablanca', 'Rabat', 'Tanger']
    )
    
    if villes_histo:
        histo_filter = historique[historique['ville'].isin(villes_histo)]
        prix_par_jour = histo_filter.groupby(['date_extraction', 'ville'])['gasoil'].mean().reset_index()
        
        fig_histo = px.line(
            prix_par_jour,
            x='date_extraction',
            y='gasoil',
            color='ville',
            title="Évolution du prix du Gasoil",
            labels={'gasoil': 'Prix (DH/L)', 'date_extraction': 'Date'}
        )
        st.plotly_chart(fig_histo, use_container_width=True)
# ========== TOP STATIONS ==========
st.subheader("🏆 Top 10 stations les moins chères")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🟢 Gasoil")
    top_gasoil = df[df['gasoil'].notna()].nsmallest(10, 'gasoil')[['enseigne', 'ville', 'gasoil', 'adresse']]
    if not top_gasoil.empty:
        st.dataframe(top_gasoil, use_container_width=True)

with col_right:
    st.markdown("### 🟢 Essence")
    top_essence = df[df['essence'].notna()].nsmallest(10, 'essence')[['enseigne', 'ville', 'essence', 'adresse']]
    if not top_essence.empty:
        st.dataframe(top_essence, use_container_width=True)

# ========== CALCULATEUR ==========
st.subheader("💰 Calculateur d'économies")

with st.expander("🔍 Calcule combien tu peux économiser"):
    litres = st.slider("Litres par plein", 20, 80, 50)
    
    villes_dispo = sorted(df[df['gasoil'].notna()]['ville'].unique())
    if villes_dispo:
        ville_choice = st.selectbox("Ville", villes_dispo)
        
        stations_ville = df[(df['ville'] == ville_choice) & (df['gasoil'].notna())]
        if not stations_ville.empty:
            prix_min = stations_ville['gasoil'].min()
            prix_max = stations_ville['gasoil'].max()
            econo_plein = (prix_max - prix_min) * litres
            
            st.metric(
                f"💰 Économie par plein à {ville_choice}",
                f"{econo_plein:.0f} DH",
                delta=f"En choisissant la station la moins chère"
            )
            st.metric(
                "📅 Économie mensuelle (4 pleins)",
                f"{econo_plein * 4:.0f} DH"
            )
            
            st.write(f"**Prix min:** {prix_min:.2f} DH/L")
            st.write(f"**Prix max:** {prix_max:.2f} DH/L")
            st.write(f"**Différence:** {(prix_max - prix_min):.2f} DH/L")

# ========== TABLEAU COMPLET ==========
with st.expander("📋 Liste complète des stations"):
    st.dataframe(df[['enseigne', 'ville', 'gasoil', 'essence', 'adresse']], use_container_width=True)