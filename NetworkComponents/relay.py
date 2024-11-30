import socket
import threading
from NetworkComponents.relay_handler import RelayHandler

class Relay:
    def __init__(self, name, bind_ip:str='localhost', bind_port=5000, hubs=[]):
        self.name = name
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((bind_ip, bind_port))
        self.server_socket.listen(5)
        print(f"Relay server listening at {bind_ip}:{bind_port}")

        self.hub_connections = {}  # Dictionary to store connections to hubs
        self.hub_names = {}
        self.lock = threading.Lock()  # Lock for thread-safe access to hub_connections
        self.hubs = hubs  # List of hubs (IP, port) to connect to

    def start(self):
        # First, connect to all the hubs
        for hub_address in self.hubs:
            self.connect_to_hub(hub_address)

    def connect_to_hub(self, hub_address):
        try:
            hub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hub_socket.connect(hub_address)
            print(f"Connected to hub at {hub_address}")
            
            # Create a RelayHandler to handle communication with this hub
            relay_handler = RelayHandler(hub_socket, hub_address, self)
            relay_handler.start()
                    
        except Exception as e:
            print(f"Error connecting to hub {hub_address}: {e}")

    def add_hub(self, hub_address, hub_socket, hub_id)->None:
        with self.lock:  # Ensure thread-safe modification
            self.hub_connections[hub_address] = hub_socket
            self.hub_names[hub_address] = hub_id

    def remove_hub(self, hub_address)->None:
        with self.lock:  # Ensure thread-safe removal
            if hub_address in self.hub_connections:
                del self.hub_connections[hub_address]
                del self.hub_names[hub_address]

    def get_active_hubs(self)->dict:
        with self.lock:  # Ensure thread-safe access
            return self.hub_connections.copy()  # Return a copy to avoid external modification

    def get_hub_name(self, hub_address)->str:
        with self.lock:
            return self.hub_names[hub_address]
        
    def get_hub_add_from_name(self, hub_name):
        with self.lock:
            for address, name in self.hub_names.items():
                if name == hub_name:
                    return address