import smtplib
import pandas as pd
from email.mime.text import MIMEText
from datetime import datetime
import os

# Configuration (à mettre dans .env)
# EMAIL_SENDER = ton_email@gmail.com
# EMAIL_PASSWORD = mot_de_passe_application
# EMAIL_RECEIVER = ton_email_reception@gmail.com

def check_price_drop(df, seuil=0.50):
    """Vérifie si les prix ont baissé de plus de seuil DH"""
    
    # Charge l'historique
    hist_file = "data/processed/historique.csv"
    if not os.path.exists(hist_file):
        return None
    
    historique = pd.read_csv(hist_file)
    
    # Dernier prix vs avant-dernier
    dernier = df[df['gasoil'].notna()].groupby('ville')['gasoil'].mean()
    
    dates = sorted(historique['date_extraction'].unique())
    if len(dates) < 2:
        return None
    
    avant_dernier = historique[historique['date_extraction'] == dates[-2]]
    avant_dernier = avant_dernier.groupby('ville')['gasoil'].mean()
    
    # Calcul des baisses
    baisses = {}
    for ville in dernier.index:
        if ville in avant_dernier.index:
            drop = avant_dernier[ville] - dernier[ville]
            if drop > seuil:
                baisses[ville] = {'baisse': drop, 'prix_actuel': dernier[ville]}
    
    return baisses

def send_alert(baisses):
    """Envoie un email d'alerte"""
    if not baisses:
        return
    
    content = f"📉 BAISSE DES PRIX DÉTECTÉE !\n\n"
    content += f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    
    for ville, data in baisses.items():
        content += f"📍 {ville}: -{data['baisse']:.2f} DH/L\n"
        content += f"   Prix actuel: {data['prix_actuel']:.2f} DH/L\n\n"
    
    # Envoi email (à configurer)
    # send_email(content)
    
    print(content)
    return content

if __name__ == "__main__":
    df = pd.read_csv("data/raw/stations_*.csv")  # Dernier fichier
    baisses = check_price_drop(df)
    send_alert(baisses)