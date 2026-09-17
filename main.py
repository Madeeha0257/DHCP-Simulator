import tkinter as tk
from tkinter import ttk

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

        return self.ip_pool[0]

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

    def release_ip(self, client_id):
        if client_id not in self.allocated_ips:
            return None

        released_ip = self.allocated_ips.pop(client_id)
        self.ip_pool.insert(0, released_ip)

        return self.release_ip

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

    if success:
        #DHCP Acknowledgement
        log_message(f"[ACK] IP {offered_ip} assigned to {client_id}")

        #Add client and IP to GUI table
        ip_table.insert("", "end", values=(client_id, offered_ip))

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
columns = ("Client ID", "Assigned IP")

ip_table = ttk.Treeview(root, columns = columns, show = "headings", height = 5)

#Configure column headings
ip_table.heading("Client ID", text="Client ID")
ip_table.heading("Assigned IP", text="Assigned IP")

#Configure column width
ip_table.column("Client ID", width = 200)
ip_table.column("Assigned IP", width = 200)

ip_table.pack(pady=10)

#Message log handling
log_label = tk.Label(root, text="DHCP Message Log", font=("Arial", 14, "bold"))
log_label.pack(pady=(20, 5))

#Message log text box
message_log = tk.Text(root, height = 8, width = 70, state = "disabled")
message_log.pack(pady=10)

#Start GUI Event loop
root.mainloop()