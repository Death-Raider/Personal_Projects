import socket
import threading
from NetworkComponents.hub_handler import ClientHandler

class Hub:
    def __init__(self, name, bind_ip:str, port:int):
        self.name = name
        self.port = port
        self.server_socket:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((bind_ip, self.port))
        print(f"server listening at port {port} on address {bind_ip}")
        self.server_socket.listen(5)
        self.clients:dict = {}
        self.clientName = {}
        self.lock = threading.Lock()  # Lock to ensure thread safety on clients dictionary

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"{client_address} connected")
            client_handler = ClientHandler(client_socket, client_address, self)
            client_handler.start()
            
    def add_client(self, client_address, client_socket, client_id)->None:
        with self.lock:  # Ensure thread-safe modification
            self.clients[client_address] = client_socket
            self.clientName[client_address] = client_id

    def remove_client(self, client_address)->None:
        with self.lock:  # Ensure thread-safe removal
            if client_address in self.clients:
                del self.clients[client_address]
                del self.clientName[client_address]

    def get_active_clients(self)->dict:
        with self.lock:  # Ensure thread-safe access
            return self.clients.copy()  # Return a copy to avoid external modification

    def get_client_name(self, client_address)->str:
        with self.lock:
            return self.clientName[client_address]
        
    def get_client_add_from_name(self, client_name):
        with self.lock:
            for address, name in self.clientName.items():
                if name == client_name:
                    return address