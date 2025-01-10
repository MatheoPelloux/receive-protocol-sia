import socket
import ssl

context = ssl.create_default_context()
secure_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname="localhost")

secure_socket.connect(('localhost', 65100))
secure_socket.sendall(b"Test message SIA")

secure_socket.close()
