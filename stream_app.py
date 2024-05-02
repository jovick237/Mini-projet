import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
import pydeck as pdk
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from folium.plugins import FastMarkerCluster

# Chargement et préparation des données
@st.cache_data
def load_and_prepare_data(filename):
    data = pd.read_csv(filename, delimiter=';', decimal=',')
    data = data.rename(columns={'long': 'lon'}) if 'long' in data.columns else data
    data['lat'] = data['lat'].astype(str).str.replace(',', '.')
    data['lon'] = data['lon'].astype(str).str.replace(',', '.')
    data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
    data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
    data.dropna(subset=['lat', 'lon'], inplace=True)
    data['hrmn'] = data['hrmn'].str.replace(':', '.').astype(float)
    data['dep'] = pd.to_numeric(data['dep'], errors='coerce')
    data['com'] = pd.to_numeric(data['com'], errors='coerce').fillna(0)
    # Supprimer la colonne 'adr' qui n'est pas nécessaire
    data = data.drop('adr', axis=1)
    return data

# Construction et entraînement du modèle
@st.cache(allow_output_mutation=True)
def build_and_train_model(data):
    features = data[['jour', 'mois', 'hrmn']]
    target = data[['lat', 'lon']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    model = Sequential([
        Input(shape=(features_scaled.shape[1],)),
        Dense(128, activation='relu'),
        Dropout(0.1),
        Dense(64, activation='relu'),
        Dropout(0.1),
        Dense(2)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.fit(features_scaled, target, epochs=20, batch_size=32, validation_split=0.2, verbose=1)
    return model, scaler

# Prédictions
@st.cache(allow_output_mutation=True)
def evaluate_model(model, scaler, input_features):
    features_scaled = scaler.transform(input_features)
    predictions = model.predict(features_scaled)
    return predictions

# Affichage des données
def show_data(df):
    st.image("paris.jpg", use_column_width=True)
    st.subheader("Affichage des Données")
    st.write(df.head())
    st.subheader("Description Statistique des Données")
    st.write(df.describe())
    
    

# Carte avec PyDeck
def show_pydeck_map(df):
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


# Carte avec Folium
def show_map_folium(df):
    st.subheader("Carte des accidents (Folium)")
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=6)

    # Utiliser FastMarkerCluster pour un chargement plus rapide
    marker_cluster = FastMarkerCluster(data=list(zip(df['lat'].dropna(), df['lon'].dropna())))
    marker_cluster.add_to(m)

    folium_static(m)

# Prédictions
def show_predictions(model, scaler):
    st.subheader("Effectuer une Prédiction")
    jour = st.number_input('Jour', min_value=1, max_value=31, value=1)
    mois = st.number_input('Mois', min_value=1, max_value=12, value=1)
    hrmn = st.slider('Heure', min_value=0.0, max_value=23.99, value=12.0)
    if st.button('Prédire'):
        input_features = pd.DataFrame([[jour, mois, hrmn]], columns=['jour', 'mois', 'hrmn'])
        predictions = evaluate_model(model, scaler, input_features)
        st.write("Prédictions de latitude et longitude :")
        st.write(predictions)
        st.image("vehi.jpg", use_column_width=True)

# Visualisations dynamiques
def show_visualizations(df, model, scaler):
    st.sidebar.subheader("MENU")
    visualization_choice = st.sidebar.radio("Choisir une Option:", ["Données", "Carte avec PyDeck", "Carte avec Folium", "Prédictions"])
    
    show_histograms = st.sidebar.checkbox("Afficher les Histogrammes")

    if visualization_choice == "Données":
        show_data(df)
    elif visualization_choice == "Carte avec PyDeck":
        show_pydeck_map(df)
    elif visualization_choice == "Carte avec Folium":
        show_map_folium(df)
    elif visualization_choice == "Prédictions":
        show_predictions(model, scaler)

    if show_histograms:
        st.subheader("Histogrammes")
        
        # Sélection du jour et du mois
        selected_day = st.sidebar.slider("Sélectionner un jour", 1, 31, 1)
        selected_month = st.sidebar.slider("Sélectionner un mois", 1, 12, 1)
        
        # Filtrage des données en fonction de la sélection de l'utilisateur
        filtered_df = df[(df['jour'] == selected_day) & (df['mois'] == selected_month)]
        
        # Affichage des histogrammes
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].hist(filtered_df['jour'], bins=20, color='skyblue', alpha=0.7)
        axes[0].set_title('Histogramme du Jour')
        axes[1].hist(filtered_df['mois'], bins=20, color='salmon', alpha=0.7)
        axes[1].set_title('Histogramme du Mois')
        axes[2].hist(filtered_df['hrmn'], bins=20, color='green', alpha=0.7)
        axes[2].set_title('Histogramme de l\'Heure')
        st.pyplot(fig)

# Fonction principale
def main():
    st.title("Prédiction des lieux d'accidents de la route")
    df = load_and_prepare_data('carcteristiques-2022.csv')
    model, scaler = build_and_train_model(df)

    show_visualizations(df, model, scaler)
    

if __name__ == "__main__":
    main()
