from NetworkComponents.client import Client
from NetworkComponents.data_packet import Packet
import time


CLIENT_NAME = 'Client1'
RECIPIENT_NAME = 'Client2'
HUB_NAME = 'hub1'

HUB_PORT = 12345
HUB_ADDRESS = 'localhost'
data = 1101


client = Client(CLIENT_NAME, HUB_PORT, HUB_ADDRESS)
client.connect()
time.sleep(2)
try:
    while True:
        message = Packet(HUB_NAME, client.name, RECIPIENT_NAME, client.name, data)
        client.send_message(message)

        response = client.receive_message(4096)
        if response:
            print(f"Received from hub: {response}")
        time.sleep(3)
except:
    client.close()