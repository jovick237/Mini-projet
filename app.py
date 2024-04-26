import requests
from bs4 import BeautifulSoup

# L'URL de la page contenant les fichiers CSV
url_page = 'https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2022/'

# Liste des catégories spécifiques qui nous intéressent
categories_interet = ['usagers', 'vehicules', 'lieux', 'carcteristiques']

# Effectuer une requête GET à l'URL
response = requests.get(url_page)

# Si la requête a réussi
if response.status_code == 200:
    # Parser le contenu de la page avec BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Créer un dictionnaire pour suivre le fichier le plus récent pour chaque catégorie
    latest_files = {category: {'year': 0, 'url': ''} for category in categories_interet}

    # Chercher tous les liens de téléchargement de fichiers CSV
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.csv'):
            filename = href.split('/')[-1]
            parts = filename.replace('.csv', '').split('-')
            if len(parts) == 2 and parts[1].isdigit() and parts[0] in categories_interet:
                category, year = parts
                # Mettre à jour le fichier le plus récent pour la catégorie donnée
                if int(year) > int(latest_files[category]['year']):
                    latest_files[category] = {'year': year, 'url': href}

    # Télécharger les fichiers CSV les plus récents pour les catégories d'intérêt
    for category, file_info in latest_files.items():
        if file_info['url']:  # S'assurer qu'il y a un lien à télécharger
            file_url = file_info['url']
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                # Écrire le contenu dans un fichier local
                with open(f"{category}-{file_info['year']}.csv", 'wb') as file:
                    file.write(file_response.content)
                print(f"Téléchargé {category}-{file_info['year']}.csv")
            else:
                print(f"Échec du téléchargement de {category}-{file_info['year']}.csv")
        else:
            print(f"Aucun fichier récent trouvé pour {category}")

else:
    print("Échec de la requête vers la page de données.")
