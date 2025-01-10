import sqlite3

def get_detectors_from_db():
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('detectors.db')
    cursor = conn.cursor()

    # Récupère tous les détecteurs
    cursor.execute("SELECT account_id, key FROM detectors")
    
    # Récupère tous les résultats de la requête
    detectors = cursor.fetchall()

    # Ferme la connexion à la base de données
    conn.close()

    # Convertit la liste de détecteurs en un dictionnaire
    return {detector[0]: {"account_id": detector[0], "key": detector[1]} for detector in detectors}

# Appel de la fonction pour récupérer les détecteurs
detectors = get_detectors_from_db()

# Afficher les détecteurs récupérés
print(detectors)
