import streamlit as st
import pandas as pd
import pydeck as pdk
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster
import matplotlib.pyplot as plt

# Fonctions de chargement des données (avec cache)
@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, delimiter=';', decimal=',',low_memory=False)
     # Renommer la colonne ici si elle est nommée 'long' dans le fichier CSV
    if 'long' in data.columns:
        data = data.rename(columns={'long': 'lon'})
    return data

# Chargement des données
df_usagers = load_data('usagers-2022.csv')
df_vehicules = load_data('vehicules-2022.csv')
df_lieux = load_data('lieux-2022.csv')
df_caracteristiques = load_data('carcteristiques-2022.csv')

# Convertir les colonnes lat et lon en numériques (si ce ne sont pas déjà des types numériques)
df_caracteristiques['lat'] = pd.to_numeric(df_caracteristiques['lat'], errors='coerce')
df_caracteristiques['lon'] = pd.to_numeric(df_caracteristiques['lon'], errors='coerce')

def show_map_folium(df):
    st.subheader("Carte des accidents (Folium)")
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=6)

    # Utiliser FastMarkerCluster pour un chargement plus rapide
    marker_cluster = FastMarkerCluster(data=list(zip(df['lat'].dropna(), df['lon'].dropna())))
    marker_cluster.add_to(m)

    folium_static(m)

# Fonction pour afficher une carte avec Pydeck
def show_map(df):
    if 'lat' in df.columns and 'lon' in df.columns:
        st.subheader("Carte des accidents (Pydeck)")
        st.write("Répartition géographique des accidents")

        # Filtrer les données pour éviter les points sans localisation
        df_localisation = df.dropna(subset=['lat', 'lon'])

        # Création de la carte
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=df_localisation['lat'].mean(),
                longitude=df_localisation['lon'].mean(),
                zoom=6,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df_localisation,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
            ],
        ))
    else:
        st.warning("Les données de localisation ne sont pas disponibles.")

def plot_dynamic_histogram(df, column):
    fig, ax = plt.subplots()
    df[column].dropna().hist(bins=20, ax=ax)
    ax.set_title(f'Histogramme Dynamique pour {column}')
    ax.set_xlabel(column)
    ax.set_ylabel('Nombre d’occurrences')
    st.pyplot(fig)

# Analyse exploratoire des données
def eda():
    st.header("Analyse exploratoire des données (EDA)")

    st.subheader("Aperçu des données sur les usagers")
    st.write(df_usagers.head())
    st.subheader("Statistiques descriptives des données sur les usagers")
    st.write(df_usagers.describe())
    st.subheader("Valeurs manquantes dans les données sur les usagers")
    st.write(df_usagers.isnull().sum())

    st.subheader("Aperçu des données sur les vehicules")
    st.write(df_vehicules.head())
    st.subheader("Statistiques descriptives des données sur les vehicules")
    st.write(df_vehicules.describe())
    st.subheader("Valeurs manquantes dans les données sur les vehicules")
    st.write(df_vehicules.isnull().sum())

    st.subheader("Aperçu des données sur les lieux")
    st.write(df_lieux.head())
    st.subheader("Statistiques descriptives des données sur les lieux")
    st.write(df_lieux.describe())
    st.subheader("Valeurs manquantes dans les données sur les lieux")
    st.write(df_lieux.isnull().sum())

    st.subheader("Aperçu des données sur les caracteristiques")
    st.write(df_caracteristiques.head())
    st.subheader("Statistiques descriptives des données sur les caracteristiques")
    st.write(df_caracteristiques.describe())
    st.subheader("Valeurs manquantes dans les données sur les caracteristiques")
    st.write(df_caracteristiques.isnull().sum())

def visualisation(df):
    st.header("Histogramme Dynamique")
    # Permettre à l'utilisateur de choisir une colonne pour l'histogramme
    if st.checkbox('Afficher Histogramme Dynamique'):
        selected_column = st.selectbox('Choisir une colonne', df_caracteristiques.columns)
        plot_dynamic_histogram(df_caracteristiques, selected_column)

# Page d'accueil
def home():
    st.title("Analyse des accidents corporels en France")
    st.markdown("""
    Bienvenue sur cette application d'analyse des accidents corporels en France. 
    Vous pouvez naviguer dans les différentes sections pour explorer les données des usagers, véhicules, lieux et caractéristiques des accidents.
    """)
    st.image('th.jpg', use_column_width=True)  # Remplacez 'logo.png' par le chemin vers votre image de logo



def verify_data(df):
    # Vérifier la qualité des données
    qualite_suffisante = df.isnull().mean().max() < 0.1  # moins de 10% de valeurs manquantes
    if not qualite_suffisante:
        st.warning("La qualité des données n'est pas suffisante.")
    
    return qualite_suffisante

# Nettoyage des données
def clean_data(df):
    # Suppression des doublons
    df.drop_duplicates(inplace=True)

    # Traitement des valeurs manquantes
    df.dropna(inplace=True)

    # Conversion des types de données, si nécessaire
    # Exemple: Convertir les colonnes 'lat' et 'lon' en numérique
    
    return df

# Menu de navigation
def main():
    menu = ["Accueil", "Analyse exploratoire", "Nettoyage des données", "Carte avec Pydeck", "Carte avec Folium","Visualisations"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Accueil":
        home()
    elif choice == "Analyse exploratoire":
        eda()
        # ... vous pouvez ajouter d'autres options si nécessaire
    elif choice == "Nettoyage des données":
        # Appel de la fonction de nettoyage pour chaque DataFrame
        clean_df_usagers = clean_data(df_usagers)
        clean_df_vehicules = clean_data(df_vehicules)
        clean_df_lieux = clean_data(df_lieux)
        clean_df_caracteristiques = clean_data(df_caracteristiques)
        
        # Vérification des données nettoyées
        if all(verify_data(df) for df in [clean_df_usagers, clean_df_vehicules, clean_df_lieux, clean_df_caracteristiques]):
            st.success("Les données sont propres et de qualité vérifiée.")
            st.subheader("Valeurs manquantes dans les données sur les usagers")
            st.write(df_usagers.isnull().sum())
            st.subheader("Valeurs manquantes dans les données sur les vehicules")
            st.write(df_vehicules.isnull().sum())
            st.subheader("Valeurs manquantes dans les données sur les lieux")
            st.write(df_lieux.isnull().sum())
            st.subheader("Valeurs manquantes dans les données sur les caracteristiques")
            st.write(df_caracteristiques.isnull().sum())
        # Utiliser les DataFrame nettoyés pour les autres analyses

    elif choice == "Carte avec Pydeck":
        show_map(df_caracteristiques)
    elif choice == "Carte avec Folium":
        show_map_folium(df_caracteristiques)
    elif choice == "Visualisations":
       # Permettre à l'utilisateur de choisir quel DataFrame explorer
        df_choice = st.selectbox('Choisir un ensemble de données', ('Usagers', 'Véhicules', 'Lieux', 'Caractéristiques'))
        if df_choice == 'Usagers':
            visualisation(df_usagers)
        elif df_choice == 'Véhicules':
            visualisation(df_vehicules)
        elif df_choice == 'Lieux':
            visualisation(df_lieux)
        elif df_choice == 'Caractéristiques':
            visualisation(df_caracteristiques)


if __name__ == "__main__":
    main()
