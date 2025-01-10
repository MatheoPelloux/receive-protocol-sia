import socket
import ssl

# Configuration
SERVER_HOST = "192.168.56.1"  # Remplacez par l'adresse de votre serveur
SERVER_PORT = 65100        # Remplacez par le port de votre serveur
MESSAGE = "1234HelloWorld"  # Exemple de message SIA (modifiez selon vos besoins)

def send_tls_message():
    try:
        # Création d'un contexte TLS
        context = ssl.create_default_context()
        
        # Connexion au serveur
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=SERVER_HOST) as secure_sock:
                print(f"[INFO] Connexion sécurisée établie avec {SERVER_HOST}:{SERVER_PORT}")
                
                # Envoi du message
                secure_sock.sendall(MESSAGE.encode('utf-8'))
                print(f"[INFO] Message envoyé : {MESSAGE}")
                
                # Réception de la réponse (si votre serveur envoie une réponse)
                response = secure_sock.recv(1024)
                print(f"[INFO] Réponse reçue : {response.decode('utf-8')}")
    except Exception as e:
        print(f"[ERREUR] Une erreur s'est produite : {e}")

if __name__ == "__main__":
    send_tls_message()
