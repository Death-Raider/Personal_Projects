import threading
import pickle
from NetworkComponents.data_packet import Packet

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address, hub):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.hub = hub  # Hub instance, to access get_active_clients method
        self.name = self.hub.name

    def check_packet_for_self(self,data:Packet):
        network_paths = data.get_network_add()
        physical = data.get_physical_add()
        print("Data Path Packet",network_paths,physical)
        net_name_condition = (network_paths['NetworkReceiver'] == self.name) and (physical['Receiver'] == self.name)
        general_identification_condition = (network_paths['NetworkReceiver'] == -1) and (physical['Receiver'] == -1)
        return network_paths, physical, net_name_condition or general_identification_condition

    def run(self):
        print("client running", self.client_socket)

        while True:
            data = self.recieve_message(4096)
            print(self.name,'received ',data)
            
            if data.network_receiver_id == 0 and data.network_sender_id == 0: # disconnect packet
                print(f'{data.data} authenticated the disconnection with {self.name}')
                break
            
            network_paths,physical,cond = self.check_packet_for_self(data)
            
            if cond: # packet is ment for hub
                # if the packet is ment for the hub then it is an self-identification packet
                self.hub.add_client(self.client_address, self.client_socket, data.data)
                print(f'{data.data} authenticated the connection with {self.name}')
                print('sending ACK')
                self.send_message(Packet(data.data, self.name, data.data, self.name, self.name), self.client_address)

            elif network_paths['NetworkReceiver'] in (self.name,-1): # packet is in transit to somewhere else
                # add network_paths['NetworkSender'] to table
                # check  physcial['Receiver'] in table
                # assuming no table, aka receiver not in table
                destination_name = physical['Receiver']
                destination_address = self.hub.get_client_add_from_name(destination_name)
                self.send_message(data, destination_address)

            else: # packet not addressed for hub to transmit
                print("Packet dropped")
                pass

        self.client_socket.close()
        print("client closed", data.data)
        self.hub.remove_client(self.client_address)  # Remove client from hub
    
    def recieve_message(self, total_bytes=1024)->Packet:
        data_bytes = self.client_socket.recv(total_bytes)
        data = pickle.loads(data_bytes)
        return data
    
    def send_message(self, data:Packet, destination_address):
        # Use the hub to get the current list of active clients
        active_clients = self.hub.get_active_clients()
        new_data = data.copy()
        print("num active clients:",len(active_clients))
        print("destination_address:", destination_address)

        if destination_address in active_clients:
            print("Client Found, forwarding message")
            new_data.network_receiver_id = self.hub.get_client_name(destination_address)
            new_data.network_sender_id = self.name
            client_socket = active_clients[destination_address]
            data_bytes = pickle.dumps(new_data)
            client_socket.sendall(data_bytes)

        else:
            print(f"Destination address {destination_address} not found. Sending to all connected clients")
            for client_address in active_clients:
                new_data.network_sender_id = self.name
                new_data.network_receiver_id = self.hub.get_client_name(client_address)
                if new_data.network_receiver_id == data.network_sender_id:
                    continue
                client_socket = active_clients[client_address]
                data_bytes = pickle.dumps(new_data)
                client_socket.sendall(data_bytes)
