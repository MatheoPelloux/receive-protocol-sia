import mysql.connector
import socket
import ssl
import json
import threading
from flask import Flask, request, jsonify
from pysiaalarm import SIAAccount, SIAClient

# Chargement de la configuration depuis un fichier JSON
def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print("[ERREUR] Fichier de configuration 'config.json' introuvable.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERREUR] Erreur de parsing du fichier de configuration : {e}")
        exit(1)

config = load_config()

# Validation de la plage de port
def validate_port(port):
    if not (0 < port <= 65535):
        raise ValueError(f"Le port spécifié ({port}) est invalide. Veuillez choisir un port entre 1 et 65535.")

validate_port(config['server']['port'])

# Configuration du serveur
HOST = config['server']['host']
PORT = config['server']['port']
CERTFILE = config['tls']['certfile']
KEYFILE = config['tls']['keyfile']

# Connexion à la base MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['name']
    )

# Récupérer les détecteurs depuis la base de données MySQL
def get_detectors_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT account_id, `key` FROM detectors")
        detectors = cursor.fetchall()
        conn.close()
        return {detector["account_id"]: {"account_id": detector["account_id"], "key": detector["key"]} for detector in detectors}
    except mysql.connector.Error as e:
        print(f"[ERREUR] Erreur MySQL : {e}")
        exit(1)

# Ajouter un détecteur dans MySQL
def add_detector_to_db(account_id, key):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO detectors (account_id, `key`) VALUES (%s, %s)", (account_id, key))
        conn.commit()
        conn.close()
        print("[INFO] Détecteur ajouté avec succès.")
    except mysql.connector.Error as e:
        print(f"[ERREUR] Erreur MySQL : {e}")

# Fonction pour récupérer le compte SIA en fonction de l'ACCOUNT_ID
def get_sia_account(account_id):
    detectors = get_detectors_from_db()
    if account_id in detectors:
        return SIAAccount(detectors[account_id]["account_id"], detectors[account_id]["key"])
    else:
        return None

# Fonction pour traiter les messages SIA
def handle_sia_message(data, address):
    print(f"\n[INFO] Message brut reçu de {address}: {data}")

    # Extraire l'ACCOUNT_ID du message
    account_id = data[:4]  # Hypothèse : l'ACCOUNT_ID est dans les 4 premiers caractères du message

    sia_account = get_sia_account(account_id)

    if sia_account is None:
        print(f"[ERREUR] Aucun détecteur trouvé avec l'ID {account_id}")
        return

    try:
        # Validation et décodage du message via pysiaalarm
        client = SIAClient(data, sia_account)
        if client.validate():
            print(f"[SUCCÈS] Message SIA valide :")
            print(f"  - Type d'événement : {client.event}")
            print(f"  - Compte source : {client.account}")
            print(f"  - Détails du message : {client.full_message}")
        else:
            print("[ERREUR] Message invalide ou problème de validation.")
    except Exception as e:
        print(f"[ERREUR] Impossible de traiter le message : {e}")

# Serveur avec TLS pour écouter les messages
def start_tls_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)  # Chargez vos fichiers de certificat

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            print(f"[INFO] Tentative de liaison sur {HOST}:{PORT}")
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)  # Permet jusqu'à 5 connexions simultanées

            print(f"[INFO] Serveur TLS en écoute sur {HOST}:{PORT}")

            while True:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"[INFO] Connexion TLS établie avec {addr}")

                    # Applique le chiffrement TLS sur la connexion
                    secure_socket = context.wrap_socket(client_socket, server_side=True)

                    # Traitement des messages SIA
                    data = secure_socket.recv(1024)
                    if data:
                        handle_sia_message(data.decode('utf-8'), addr)

                    secure_socket.close()
                except KeyboardInterrupt:
                    print("\n[INFO] Arrêt du serveur TLS demandé par l'utilisateur.")
                    break
                except Exception as e:
                    print(f"[ERREUR] Une erreur s'est produite : {e}")
        finally:
            print("[INFO] Fermeture du serveur...")

# API REST avec Flask
app = Flask(__name__)

@app.route('/add_detector', methods=['POST'])
def add_detector():
    data = request.get_json()
    if not data or 'account_id' not in data or 'key' not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        add_detector_to_db(data['account_id'], data['key'])
        return jsonify({"message": "Detector added successfully"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500

# Lancer Flask dans un thread séparé
def start_api_server():
    app.run(host="0.0.0.0", port=5000)

# Démarrage des serveurs
if __name__ == "__main__":
    try:
        api_thread = threading.Thread(target=start_api_server, daemon=True)
        api_thread.start()
        start_tls_server()
    except KeyboardInterrupt:
        print("\n[INFO] Programme arrêté proprement.")
