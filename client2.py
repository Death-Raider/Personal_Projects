from NetworkComponents.client import Client
from NetworkComponents.data_packet import Packet
import time


CLIENT_NAME = 'Client2'
RECIPIENT_NAME = 'Client1'
HUB_NAME = 'hub2' # -1 if hub_name is not known else hub_name ('hub1') 

HUB_PORT = 54321
HUB_ADDRESS = 'localhost'
data = '0010'


client = Client(CLIENT_NAME, HUB_PORT, HUB_ADDRESS)
client.connect()
time.sleep(2)

try:
    while True:
        response = client.receive_message(4096)
        if response:
            print(f"Received: {response}")
            message = Packet(HUB_NAME, client.name, RECIPIENT_NAME, client.name, data)
            client.send_message(message)
except Exception as e:
    print(e)
    client.close()