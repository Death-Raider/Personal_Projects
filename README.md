# Networking Components using Python Sockets  

## **Overview**  
This project is an exploration of network communication using Python sockets, showcasing basic networking devices such as **Hub**, **Relay/Switch**, and **Client/Server**. The primary goal is to simulate and understand the working of networking components and their communication mechanisms.  

---

## **File Structure**  

```
Network Components  
|   ├── hub_handler.py  
|   ├── hub.py  
|   ├── relay_handler.py  
|   ├── relay.py  
|   ├── client.py  
|   ├── data_packet.py  
├── client1.py  
├── client2.py  
├── server1.py  
├── server2.py  
├── relay1.py  
├── README.md  
```  

---

## **Key Components**  

### 1. **Hub**  
- Acts as a network device that accepts multiple connections from clients or relays.  
- Each new connection is handed off to a **hub_handler** running on a separate thread.  
- **Functionality**:  
  - Broadcasts incoming packets to connected devices based on routing table.

---

### 2. **Relay**  
- Connects to hubs and serves as an intermediary device.  
- Each connection is managed by a separate thread through the **relay_handler**.  
- Threads can communicate among themselves and share a dynamic list of connections.  
- **Functionality**:  
  - Implements **flood-fill-based pathfinding** to propagate data packets through hubs.
  - Broadcasts incoming packets to connected devices based on routing table.

---

### 3. **Custom Transport Layer Protocol**  
A wrapper protocol built over the UDP data transfer layer, offering custom features:  

#### **Custom Data Packet Class**  
- Defines packets with the following fields:  
  `(network_receiver_id, network_sender_id, receiver_id, sender_id, data)`  
- Enables flexible and structured data transfer.  

#### **Packet Types**  
- **Disconnection Packet**: `(0, 0, 0, 0, -1)`  
  - Signals disconnection of a client or relay.  

- **Authentication Packet**: `(0, self_name, 0, self_name, self_name)`  
  - Used for authentication during connection setup.  

- **Auth Receive Packet**: `(recv_name, sender_name, recv_name, sender_name, sender_name)`  
  - Confirms authentication details.  

---

## **Demonstrated Features**  
1. **Thread-based Connection Management**  
   - Each device uses threads for handling connections and routing messages.  

2. **Dynamic Connection List**  
   - Hub and relay threads share a dynamic list of active connections, allowing seamless communication.  

3. **Flood-fill Pathfinding**  
   - Implements a basic broadcast mechanism to propagate packets through the network.  

4. **Custom Transport Layer**  
   - Wraps UDP packets to include additional metadata for packet type, authentication, and routing.  

---

## **Limitations**  
- **Security**:  
  - Lacks proper encryption for secure data transfer.  
  - Minimal authentication mechanism.  

- **Routing**:  
  - No routing optimization or graph-based pathfinding.  
  - Relies solely on **flood-fill**, leading to inefficiencies.  

- **Transport Layer**:  
  - No retransmission mechanism for lost packets.  
  - No congestion control or queuing system.  

---

## **Future Improvements**  

### 1. **Transport Layer Robustness**  
- Implement **encryption** for secure communication.  
- Add **data retransmission** for packet delivery assurance.  

### 2. **Routing**  
- Use **graph-based routing algorithms** like Dijkstra's or A* for optimal pathfinding.  
- Build a **routing table** for efficient forwarding decisions.  

### 3. **Network Performance Enhancements**  
- Introduce **congestion detection** and **queuing mechanisms** to manage traffic.  
- Implement **rate limiting** to prevent overloading the network.  

---

This project serves as a foundational implementation to understand the working of basic networking components and custom transport layers, offering a platform for further research and development into robust network simulation and communication protocols.