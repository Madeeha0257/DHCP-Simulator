class DHCPServer:
    def __init__(self):
        self.ip_pool = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.1.103",

        ]

        self.allocated_ips = {}

    #Simulating DHCP Discover
    def discover(self, client_id):
        print(f"\n[DISCOVER] Client {client_id} is requesting an IP.")

        if client_id in self.allocated_ips:
            ip = self.allocated_ips[client_id]

            print(f"[INFO] Client already has IP: {ip}")

            return ip

        if len(self.ip_pool) == 0:
            print("[ERROR] No available IP addresses.")

            return None

        offered_ip = self.ip_pool[0]

        print(f"[OFFER] Server offers IP: {offered_ip}")

        return offered_ip

    #Simulating DHCP Request
    def request(self, client_id, requested_ip):

        print(f"[REQUEST] Client {client_id} req")

        if requested_ip not in self.ip_pool:
            print("IP Address is not available")

            return False

        self.ip_pool.remove(requested_ip)

        self.allocated_ips[client_id] = requested_ip

        print(f"[ACK] IP {requested_ip} assigned to {client_id}")

        return True

#Create a DHCP Server
server = DHCPServer()

#Simulate Client 1
server.discover("Client-1")
server.request("Client-1", "192.168.1.100")

#Simulate Client2
server.discover("Client-2")
server.request("Client-2", "192.168.1.101")

#Display Results
print("\nAllocated IPs:")
print(server.allocated_ips)

print("\nAvailable IPs:")
print(server.ip_pool)
        

         
