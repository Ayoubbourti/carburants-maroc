import requests
import pandas as pd
from datetime import datetime
import json
import os

API_URL = "https://prix-gasoil-maroc.teraedge.ma/api/stations"

def fetch_stations():
    """Récupère toutes les stations depuis l'API"""
    print("🌐 Récupération des stations...")
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        stations = data.get('stations', [])
        print(f"✅ {len(stations)} stations récupérées")
        return stations
    else:
        print(f"❌ Erreur: {response.status_code}")
        return []

def transform_to_dataframe(stations):
    """Transforme les données en DataFrame"""
    records = []
    
    for station in stations:
        # Extraction des prix
        prices = station.get('prices', {})
        gasoil = prices.get('gazole')
        essence = prices.get('essence')
        
        # Déterminer l'enseigne à partir du nom
        name = station.get('name', '')
        enseigne = "Autre"
        if "Shell" in name:
            enseigne = "Shell"
        elif "Total" in name or "TotalEnergies" in name:
            enseigne = "TotalEnergies"
        elif "Afriquia" in name:
            enseigne = "Afriquia"
        elif "Winxo" in name:
            enseigne = "Winxo"
        elif "Petrom" in name:
            enseigne = "Petromin"
        elif "OLA" in name:
            enseigne = "OLA Energy"
        
        # Extraire la ville depuis l'adresse ou les coordonnées
        address = station.get('address', '')
        # Essayer de trouver la ville dans l'adresse
        villes_connues = ['Casablanca', 'Rabat', 'Tanger', 'Agadir', 'Marrakech', 
                          'Fes', 'Meknès', 'Oujda', 'Kénitra', 'Tétouan', 'Safi', 
                          'Mohammedia', 'El Jadida', 'Beni Mellal', 'Nador', 'Témara']
        ville = "Autre"
        for v in villes_connues:
            if v.lower() in address.lower():
                ville = v
                break
        
        records.append({
            'id': station.get('id'),
            'nom': name,
            'enseigne': enseigne,
            'adresse': address,
            'ville': ville,
            'latitude': station.get('latitude'),
            'longitude': station.get('longitude'),
            'gasoil': gasoil if gasoil else None,
            'essence': essence if essence else None,
            'date_extraction': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(records)
    
    # Statistiques
    stations_avec_gasoil = df['gasoil'].notna().sum()
    stations_avec_essence = df['essence'].notna().sum()
    
    print(f"📊 Stations avec prix gasoil: {stations_avec_gasoil}")
    print(f"📊 Stations avec prix essence: {stations_avec_essence}")
    
    return df

def save_data(df):
    """Sauvegarde les données"""
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Sauvegarde CSV
    csv_file = f"data/raw/stations_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"💾 CSV sauvegardé: {csv_file}")
    
    # Mise à jour historique
    hist_file = "data/processed/historique.csv"
    if os.path.exists(hist_file):
        historique = pd.read_csv(hist_file)
        df_final = pd.concat([historique, df], ignore_index=True)
    else:
        df_final = df
    
    df_final.to_csv(hist_file, index=False)
    print(f"📊 Historique: {len(df_final)} enregistrements")
    
    return df_final

def get_villes_summary(df):
    """Résumé par ville"""
    summary = df[df['gasoil'].notna()].groupby('ville').agg({
        'gasoil': ['mean', 'min', 'max', 'count']
    }).round(2)
    summary.columns = ['prix_moyen', 'prix_min', 'prix_max', 'nb_stations']
    return summary

if __name__ == "__main__":
    print("="*50)
    print("⛽ EXTRACTION PRIX CARBURANTS MAROC")
    print("="*50)
    
    stations = fetch_stations()
    if stations:
        df = transform_to_dataframe(stations)
        df_final = save_data(df)
        
        print("\n📊 RÉSUMÉ PAR VILLE:")
        print(get_villes_summary(df))
        
        # Afficher les stations les moins chères
        print("\n🏆 TOP 5 STATIONS LES MOINS CHÈRES (GASOIL):")
        top = df[df['gasoil'].notna()].nsmallest(5, 'gasoil')
        for _, row in top.iterrows():
            print(f"   {row['enseigne']} - {row['ville']}: {row['gasoil']} DH/L")