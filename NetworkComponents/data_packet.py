class Packet:
    def __init__(self, network_receiver_id, network_sender_id, receiver_id, sender_id, data):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.network_sender_id = network_sender_id
        self.network_receiver_id = network_receiver_id
        self.data = data
    
    def __str__(self):
        out_str = f"{self.network_sender_id} --to--> {self.network_receiver_id}"
        return out_str
    
    def get_network_add(self):
        return {
            "NetworkReceiver":self.network_receiver_id,
            "NetworkSender":self.network_sender_id
        }
    
    def get_physical_add(self):
        return {
            "Receiver":self.receiver_id,
            "Sender":self.sender_id
        }
    
    def copy(self):
        return Packet(self.network_receiver_id,
                      self.network_sender_id,
                      self.receiver_id,
                      self.sender_id,
                      self.data)