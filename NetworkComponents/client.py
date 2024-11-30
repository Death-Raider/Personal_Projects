import socket
import pickle
from NetworkComponents.data_packet import Packet

class Client:
    def __init__(self, name, port, address):
        self.name = name
        self.port = port
        self.address = address
        self.socket = None
        self.receive_timeout = 5.0

    def connect(self,hub_name=None):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.address, self.port))
            print(f"Client {self.name} connected to hub server at {self.address}:{self.port}")
            hub_name_resolved = hub_name if hub_name != None else -1
            self.send_message(Packet(hub_name_resolved, self.name, hub_name_resolved, self.name, self.name)) # identification packet

        except ConnectionError as e:
            print(f"Connection error: {e}")
            self.socket = None

    def send_message(self, packet:Packet):
        if not self.socket:
            print(f"Client {self.name} is not connected to a hub server.")
            return None
        
        try:
            encoded_message = pickle.dumps(packet)
            self.socket.sendall(encoded_message)
            print(f"Client: {self.name} Sent: {packet}")

        except (ConnectionError, BrokenPipeError) as e:
            print(f"Error sending message: {e}")
            self.close()  # Close connection if an error occurs

    def receive_message(self, buffer_size=1024):
        if not self.socket:
            print(f"Client: {self.name} is not connected to a hub server.")
            return None

        try:
            # self.socket.settimeout(self.receive_timeout)
            data = self.socket.recv(buffer_size)
            # self.socket.settimeout(None)

            if not data:
                print(f"Client: {self.name} disconnected from hub server.")
                self.close()
                return None
            
            packet: Packet = pickle.loads(data)

            if packet.get_network_add()['NetworkReceiver'] == self.name and packet.get_physical_add()['Receiver'] == self.name:
                print("Packet Accepted: ",packet.get_physical_add())
                return packet.data
            
            print("Packet Rejected")
            return None
        
        except (ConnectionError, BrokenPipeError) as e:
            print(f"Error receiving message: {e}")
            self.close()
            return None

    def close(self):
        """
        Closes the connection to the hub server.
        """
        self.send_message(Packet(0,0,0,0,self.name)) # send disconnection packet

        if self.socket:
            self.socket.close()
            self.socket = None
            print(f"Client: {self.name} disconnected from hub server.")
