import json
import os
from pysiaalarm import SIAClient, SIAAccount
import time
from flask import Flask, jsonify, request, abort
from multiprocessing import Process

# Configuration des paramètres
HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 8421       # Port UDP sur lequel le client écoute
ACCOUNT_ID = 'SIA:#61007819-002'  # ID de compte utilisé pour l'authentification
JSON_FILE = 'sia_logs.json'  # Nom du fichier JSON où seront sauvegardés les logs
MAX_FILE_SIZE = 1 * 1024 * 1024  # Limite de taille du fichier JSON (1 Mo)

# Création de l'objet SIAAccount sans clé
account = SIAAccount(account_id=ACCOUNT_ID)

# Création du client SIA avec les paramètres nécessaires
client = SIAClient(
    host=HOST,
    port=PORT,
    function='listen',  # Fonction à exécuter, ici nous voulons écouter les messages
    accounts=[account]  # Liste des comptes autorisés à interagir avec le serveur SIA
)

# Charger les logs existants ou créer un fichier si inexistant
def load_logs():
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Sauvegarder les logs dans le fichier JSON
def save_logs(logs):
    with open(JSON_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

# Liste blanche des adresses IP
WHITELIST_IPS = [
    "135.125.9.162", "135.125.97.120",  # eu.reconeyez.com
    "209.97.141.119", "206.189.244.110", "159.249.29.188", "166.128.65", "188.166.129.36",  # uk.reconeyez.com
    "167.71.3.59",  # demo.reconeyez.com
    "104.131.39.97"  # na.reconeyez.com
]

# Fonction pour gérer les messages reçus
def handle_message(message):
    client_ip = message.sender_ip
    if client_ip not in WHITELIST_IPS:
        print(f"Connexion refusée pour l'adresse IP : {client_ip}")
        return

    logs = load_logs()
    
    # Exemple de message brut
    raw_message = message.message
    
    # Extraction des informations du message brut
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),  # Utiliser l'horodatage actuel
        "message_id": extract_message_id(raw_message),
        "type": extract_type(raw_message),
        "device_id": extract_device_id(raw_message),
        "device_type": extract_device_type(raw_message),
        "status": extract_status(raw_message),
        "alert_code": extract_alert_code(raw_message),
        "priority": extract_priority(raw_message),
        "user_id": extract_user_id(raw_message),
        "location": extract_location(raw_message),
        "checksum": extract_checksum(raw_message),
    }
    logs.append(log_entry)  # Ajouter l'entrée au fichier des logs

    # Afficher le message reçu dans la console
    print("Message reçu :", log_entry)

    # Sauvegarder les logs dans un fichier JSON
    save_logs(logs)

# Fonctions d'extraction (à implémenter selon le format de votre message brut)
def extract_message_id(raw_message):
    # Implémentez la logique pour extraire l'ID du message
    pass

def extract_type(raw_message):
    # Implémentez la logique pour extraire le type de message
    pass

def extract_device_id(raw_message):
    # Implémentez la logique pour extraire l'ID de l'appareil
    pass

def extract_device_type(raw_message):
    # Implémentez la logique pour extraire le type d'appareil
    pass

def extract_status(raw_message):
    # Implémentez la logique pour extraire le statut
    pass

def extract_alert_code(raw_message):
    # Implémentez la logique pour extraire le code d'alerte
    pass

def extract_priority(raw_message):
    # Implémentez la logique pour extraire la priorité
    pass

def extract_user_id(raw_message):
    flask_process.start()
    # Implémentez la logique pour extraire l'ID de l'utilisateur
    pass

def extract_location(raw_message):
    # Implémentez la logique pour extraire la localisation
    pass

def extract_checksum(raw_message):
    # Implémentez la logique pour extraire le checksum
    pass

# Démarrer l'écoute des messages avec la méthode appropriée
def start_sia_server():
    try:
        print(f"Serveur SIA démarré sur {HOST}:{PORT}")  # Afficher un message pour indiquer que le serveur a démarré
        client.run()  # Lancer l'écoute avec la méthode `run()` du client SIA
        print("Serveur en écoute...")  # Afficher ce message pour vérifier si le serveur reste en écoute
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur : {e}")  # Afficher une erreur si le serveur ne démarre pas
        input("Appuyez sur Entrée pour fermer...")

# Configuration du serveur Flask
app = Flask(__name__)

# Middleware pour bloquer les connexions HTTPS
@app.before_request
def enforce_http():
    if request.scheme == 'https' or 'https' in request.url:
        return jsonify({"error": "HTTPS n'est pas supporté. Veuillez utiliser HTTP."}), 400

# Route pour obtenir les logs en format JSON
@app.route('/logs', methods=['GET'])
def get_logs():
    logs = load_logs()  # Charger les logs
    return jsonify(logs)  # Retourner les logs sous forme JSON

# Démarrer le serveur Flask
def start_flask_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 4500)))

# Démarrer les serveurs SIA et Flask dans des processus séparés
if __name__ == '__main__':
    sia_process = Process(target=start_sia_server)
    flask_process = Process(target=start_flask_server)

    sia_process.start()
    flask_process.start()

    sia_process.join()
    flask_process.join()


    sia_process.join()
    flask_process.join()
