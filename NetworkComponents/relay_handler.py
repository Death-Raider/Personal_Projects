import threading
import pickle
from NetworkComponents.data_packet import Packet


class RelayHandler(threading.Thread):
    def __init__(self, hub_socket, hub_address, relay):
        threading.Thread.__init__(self)
        self.relay = relay
        self.hub_address = hub_address
        self.hub_socket = hub_socket
        self.name = self.relay.name
        print(f"RelayHandler created for hub by {self.name}")
        self.hostname = -1
        
        data_bytes = pickle.dumps(Packet(self.hostname,self.name,self.hostname,self.name,self.name))
        hub_socket.sendall(data_bytes)
        data = self.receive_message(4096)
        *_, cond = self.check_packet_for_self(data)
        
        if cond:
            self.hostname = data.data
            self.relay.add_hub(self.hub_address, self.hub_socket, self.hostname)

    def check_packet_for_self(self,data:Packet):
        network_paths = data.get_network_add()
        physical = data.get_physical_add()
        print("Data Path Packet",network_paths,physical)
        relay_name_condition = (network_paths['NetworkReceiver'] == self.name) and (physical['Receiver'] == self.name)
        general_identification_condition = (network_paths['NetworkReceiver'] == -1) and (physical['Receiver'] == -1)
        return network_paths, physical, relay_name_condition or general_identification_condition

    def run(self):
        print(f"Started RelayHandler for {self.name}")
        while True:
            try:
                # Receive data from the hub
                data = self.receive_message(4096)
                print(self.name,'received ',data)

                network_paths, physical, cond = self.check_packet_for_self(data)
                if cond: # packet is ment for hub
                    # if the packet is ment for the hub then it is an self-identification packet
                    self.relay.add_hub(self.hub_address, self.hub_socket, data.data)
                    print(f'{data.data} authenticated the connection with {self.name}')
                    print('sending ACK')
                    self.send_message(Packet(data.data, self.name, data.data, self.name, self.name), self.hub_address)

                elif network_paths['NetworkReceiver'] in (self.name,-1): # packet is in transit to somewhere else
                    # add network_paths['NetworkSender'] to table
                    # check  physcial['Receiver'] in table
                    # assuming no table, aka receiver not in table
                    destination_name = physical['Receiver']
                    destination_address = self.relay.get_hub_add_from_name(destination_name)
                    self.send_message(data, destination_address)

                else: # packet not addressed for hub to transmit
                    print("Packet dropped")
                    pass

            except Exception as e:
                print(f"Error while handling data from hub {self.name}: {e}")
                break

        self.hub_socket.close()
        print("hub closed", data.data)
        self.relay.remove_hub(self.hub_address)
        
    def receive_message(self, total_bytes=1024)->Packet:
        data_bytes = self.hub_socket.recv(total_bytes)
        data = pickle.loads(data_bytes)
        return data

    def send_message(self, data:Packet, destination_address):
        # Use the relay to get the current list of active hubs
        active_hubs = self.relay.get_active_hubs()
        new_data = data.copy()
        print("num active hubs:",len(active_hubs))
        print("destination_address:", destination_address)

        if destination_address in active_hubs:
            print("hub Found, forwarding message")
            new_data.network_receiver_id = self.relay.get_hub_name(destination_address)
            new_data.network_sender_id = self.name
            hub_socket = active_hubs[destination_address]
            data_bytes = pickle.dumps(new_data)
            hub_socket.sendall(data_bytes)

        else:
            print(f"Destination address {destination_address} not found. Sending to all connected hubs")
            for hub_address in active_hubs:
                new_data.network_sender_id = self.name
                new_data.network_receiver_id = self.relay.get_hub_name(hub_address)
                if new_data.network_receiver_id == data.network_sender_id:
                    continue
                hub_socket = active_hubs[hub_address]
                data_bytes = pickle.dumps(new_data)
                hub_socket.sendall(data_bytes)