import tkinter as tk
from tkinter import ttk
import time
import random

class DHCPServer:
    def __init__(self):
        self.ip_pool = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.1.103",
        ]

        self.allocated_ips = {}
        self.leases = {}
        self.client_macs = {}
        self.lease_duration = 20

    def generate_mac_address(self):
        mac_parts = []

        for _ in range(6):
            mac_parts.append(f"{random.randint(0, 255):02X}")

        return ":".join(mac_parts)

    def get_mac_address(self, client_id):
        if client_id not in self.client_macs:
            self.client_macs[client_id] = self.generate_mac_address()

        return self.client_macs[client_id]

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

        # If client has IP, renew its lease
        if client_id in self.allocated_ips:
            existing_ip = self.allocated_ips[client_id]

            if existing_ip == requested_ip:
                self.leases[client_id] = time.time() + self.lease_duration

                print(f"[RENEW] Lease renewed for {client_id}")
                return True

        if requested_ip not in self.ip_pool:
            print("IP Address is not available")
            return False

        self.ip_pool.remove(requested_ip)
        self.allocated_ips[client_id] = requested_ip

        #Store lease expiry time
        self.leases[client_id] = time.time() + self.lease_duration

        print(f"[ACK] IP {requested_ip} assigned to {client_id}")

        return True

    def release_ip(self, client_id):
        if client_id not in self.allocated_ips:
            return None

        released_ip = self.allocated_ips.pop(client_id)
        self.leases.pop(client_id, None)
        self.ip_pool.insert(0, released_ip)

        return released_ip

    def get_remaining_time(self, client_id):
        if client_id not in self.leases:
            return 0

        remaining_time = int(self.leases[client_id] - time.time())

        return max(0, remaining_time)

    def check_expired_leases(self):
        expired_clients = []

        for client_id in list(self.allocated_ips.keys()):
            if self.get_remaining_time(client_id) <= 0:
                expired_clients.append(client_id)

        return expired_clients


def log_message(message):
    message_log.config(state = "normal")
    message_log.insert(tk.END, message + "\n")
    message_log.config(state = "disabled")
    message_log.see(tk.END)

def request_ip():
    client_id = client_entry.get()

    if client_id == "":
        log_message("[ERROR] Please enter a Client ID.")
        return

    #DHCP Discover
    log_message(f"[DISCOVER] Client {client_id} is requesting an IP")
    offered_ip = server.discover(client_id)

    if offered_ip is None:
        log_message("[ERROR] No available IP addresses")
        return

    #DHCP Offer
    log_message(f"[OFFER] Server offers IP: {offered_ip}")

    #DHCP Request
    log_message(f"[REQUEST] Client {client_id} requests {offered_ip}")

    success = server.request(client_id, offered_ip)

    mac_address = server.get_mac_address(client_id)

    if success:

        #Add client, IP, remaining time to GUI table
        remaining_time = server.get_remaining_time(client_id)

        #If client already exists, update its row
        if ip_table.exists(client_id):
            ip_table.item(client_id, values = (client_id, mac_address, offered_ip, f"{remaining_time} seconds"))
            log_message(f"[RENEW] Lease renewed for {client_id}")
        else:
            #DHCP Acknowledgement
            log_message(f"[ACK] IP {offered_ip} assigned to {client_id}")
            ip_table.insert("", "end", iid = client_id, values=(client_id, mac_address, offered_ip, f"{remaining_time} seconds"))

        #Clear the input box
        client_entry.delete(0, tk.END)

    else:
        log_message("[NAK] IP address is not available")

def release_selected_ip():
    selected_item = ip_table.selection()

    if not selected_item:
        log_message("[ERROR] Please select a client to release its IP")
        return

    item = selected_item[0]
    client_id = ip_table.item(item, "values")[0]

    released_ip = server.release_ip(client_id)

    if released_ip is not None:
        ip_table.delete(item)
        log_message(f"[RELEASE] Client {client_id} released IP Address {released_ip}")
    else:
        log_message(f"[ERROR] No IP allocation found for client {client_id}")

def update_leases():
    expired_clients = server.check_expired_leases()

    for client_id in expired_clients:
        expired_ip = server.release_ip(client_id)

        if ip_table.exists(client_id):
            ip_table.delete(client_id)

        log_message(f"[EXPIRED] Lease for {client_id} expired")

        log_message(f"[RELEASE] IP Address {expired_ip} returned to the pool")

    #Update remaining lease time in the tabl
    for client_id in list(server.allocated_ips.keys()):
        if ip_table.exists(client_id):
            item_values = ip_table.item(client_id, "values")

            mac_address = item_values[1]
            ip_address = item_values[2]
            remaining_time = server.get_remaining_time(client_id)

            ip_table.item(client_id, values = (client_id, mac_address, ip_address, f"{remaining_time} seconds"))

    root.after(1000, update_leases)

#Create DHCP Server
server = DHCPServer()

#Main Application Window
root = tk.Tk()

#window Title
root.title("DHCP Simulator")

#Window size
root.geometry("700x500")

#Preventing small resizing
root.minsize(500,400)

#Creating a heading
title_label = tk.Label(root, text = "DHCP Simulator", font = ("Arial", 20, "bold"))
title_label.pack(pady=20)

#Creating a subtitle
subtitle_label = tk.Label(root, text = "Dynamic Host Configuration Protocol Simulation", font = ("Arial", 11))

subtitle_label.pack()

#Client ID label
client_label = tk.Label(root, text = "Enter Client ID:", font = ("Arial", 12))
client_label.pack(pady=(30,5))

#Client ID Input box
client_entry = tk.Entry(root, font = ("Arial"), width=30)
client_entry.pack(pady=5)

#Request IP button
request_button = tk.Button(root, text="Request IP Address", font = ("Arial", 12), width = 20, command = request_ip)
request_button.pack(pady=15)

#Release IP button
release_button = tk.Button(root, text = "Release Selected IP", command = release_selected_ip)
release_button.pack(pady=5)

#Allocated IP table heading
table_label = tk.Label(root, text = "Allocated IP Addresses", font = ("Arial", 14, "bold"))
table_label.pack(pady=(20, 5))

#Create the table
columns = ("Client ID", "MAC Address", "Assigned IP", "Lease Remaining")

ip_table = ttk.Treeview(root, columns = columns, show = "headings", height = 5)

#Configure column headings
ip_table.heading("Client ID", text="Client ID")
ip_table.heading("MAC Address", text = "MAC Address")
ip_table.heading("Assigned IP", text="Assigned IP")
ip_table.heading("Lease Remaining", text = "Lease Remaining")

#Configure column width
ip_table.column("Client ID", width = 130)
ip_table.column("MAC Address", width = 180)
ip_table.column("Assigned IP", width = 150)
ip_table.column("Lease Remaining", width = 150)
ip_table.pack(pady=10)

#Message log handling
log_label = tk.Label(root, text="DHCP Message Log", font=("Arial", 14, "bold"))
log_label.pack(pady=(20, 5))

#Message log text box
message_log = tk.Text(root, height = 8, width = 70, state = "disabled")
message_log.pack(pady=10)

#Start automatic lease checking
root.after(1000, update_leases)

#Start GUI Event loop
root.mainloop()