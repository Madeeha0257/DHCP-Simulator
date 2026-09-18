import tkinter as tk
from tkinter import ttk
import time
import random

class DHCPServer:
    def __init__(self):
        self.server_ip = "192.168.1.1"
        self.subnet_mask = "255.255.255.0"
        self.gateway = "192.168.1.1"
        self.dns_server = "8.8.8.8"

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

        print(f"[REQUEST] Client {client_id} requests {requested_ip}")

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

def clear_message_log():
    message_log.config(state = "normal")
    message_log.delete("1.0", tk.END)
    message_log.config(state = "disabled")

def request_ip():
    client_id = client_entry.get().strip()

    if client_id == "":
        log_message("[ERROR] Please enter a Client ID.")
        return

    if ip_table.exists(client_id):
        log_message(f"[ERROR] Client {client_id} already has an IP address")
        return

    #Get or generate client's MAC Address
    mac_address = server.get_mac_address(client_id)

    #DHCP Discover
    log_message(f"[DISCOVER] Client {client_id} is requesting an IP")
    log_message(f"           Client MAC: {mac_address}")

    offered_ip = server.discover(client_id)

    if offered_ip is None:
        log_message("[ERROR] No available IP addresses")
        return

    #DHCP Offer
    log_message(f"[OFFER] Server offers IP: {offered_ip}")
    log_message(f"         Server IP: {server.server_ip}")

    #DHCP Request
    log_message(f"[REQUEST] Client {client_id} requests {offered_ip}")
    log_message(f"          Client MAC: {mac_address}")

    success = server.request(client_id, offered_ip)

    if success:

        #Add client, IP, remaining time to GUI table
        remaining_time = server.get_remaining_time(client_id)
    
        #If client already exists, update its row
        if ip_table.exists(client_id):
            ip_table.item(client_id, values = (client_id, mac_address, offered_ip, f"{remaining_time} seconds"))
            log_message(f"[ACK] Lease renewed for {client_id}")
            log_message(f"      IP Address: {offered_ip}")
            log_message(f"      Lease Duration: {server.lease_duration} seconds")
        else:
            log_message(f"[ACK] IP {offered_ip} assigned to {client_id}")
            log_message(f"      Lease Duration: {server.lease_duration} seconds")
            
            ip_table.insert("", "end", iid = client_id, values=(client_id, mac_address, offered_ip, f"{remaining_time} seconds"))

        #Clear the input box
        client_entry.delete(0, tk.END)

    else:
        log_message("[NAK] IP address is not available")

def show_client_configuration():
    selected_item = ip_table.selection()

    if not selected_item:
        log_message("[ERROR] Please select a client to view configuration")
        return 

    item = selected_item[0]
    values = ip_table.item(item, "values")

    client_id = values[0]
    mac_address = values[1]
    assigned_ip = values[2]

    remaining_time = server.get_remaining_time(client_id)

    #Create new window for configuration details
    configuration_window = tk.Toplevel(root)
    configuration_window.title("Client Configuration")
    configuration_window.geometry("500x400")
    configuration_window.configure(bg=BG_COLOR)

    #Window heading
    configuration_label = tk.Label(configuration_window, text = "Client Configuration", font = ("Arial", 16, "bold"), bg = BG_COLOR, fg = BLUE_COLOR)

    configuration_text = (
        "Client Configuration\n"
        f"Client ID:           {client_id}\n"
        f"MAC Address:         {mac_address}\n"
        f"Assigned IP:         {assigned_ip}\n"
        f"Subnet Mask:         {server.subnet_mask}\n"
        f"Default Gateway:     {server.gateway}\n"
        f"DNS Server:          {server.dns_server}\n"
        f"Lease Duration:      {server.lease_duration} seconds\n"
        f"Lease Remaining:     {remaining_time} seconds\n"
    )

    #Text box inside new window
    configuration_log = tk.Text(configuration_window, height = 12, width = 55, state = "normal", bg = LOG_COLOR, fg = "#E2E8F0", relief="flat")
    configuration_log.pack(padx = 20, pady = 10)

    configuration_log.insert(tk.END, configuration_text)

    configuration_log.config(state = "disabled")

    #Close button
    close_button = tk.Button(configuration_window, text = "Close", font = ("Arial", 10, "bold"), bg = RED_COLOR, fg = "white", activebackground="#B91C1C", activeforeground="white", relief="flat", cursor = "hand2", command = configuration_window.destroy)
    close_button.pack(pady=10)

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
root.geometry("800x800")

#Preventing small resizing
root.minsize(600,650)

#Colour theme
BG_COLOR = "#0F172A"          # Dark navy
CARD_COLOR = "#1E293B"        # Slate
TEXT_COLOR = "#E2E8F0"        # Light text
SUBTEXT_COLOR = "#94A3B8"     # Grey text
BLUE_COLOR = "#2563EB"        # Blue
GREEN_COLOR = "#16A34A"       # Green
RED_COLOR = "#DC2626"         # Red
PURPLE_COLOR = "#7C3AED"      # Purple
INPUT_COLOR = "#334155"       # Input background
LOG_COLOR = "#020617"         # Almost black

root.configure(bg = BG_COLOR)
#Creating a heading
title_label = tk.Label(root, text = "DHCP Simulator", font = ("Arial", 20, "bold"), bg = BG_COLOR, fg = BLUE_COLOR)
title_label.pack(pady=(25, 5))

#Creating a subtitle
subtitle_label = tk.Label(root, text = "Dynamic Host Configuration Protocol Simulation", font = ("Arial", 11), bg = BG_COLOR, fg = SUBTEXT_COLOR)
subtitle_label.pack()

#Client ID label
client_label = tk.Label(root, text = "Enter Client ID:", font = ("Arial", 12), bg = BG_COLOR, fg = TEXT_COLOR)
client_label.pack(pady=(30,5))

#Client ID Input box
client_entry = tk.Entry(root, font = ("Arial"), width=30, bg = INPUT_COLOR, fg = "white", insertbackground = "white", relief = "flat", justify = "center")
client_entry.pack(pady=5)

#Button frame
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=15)

#Request IP button
request_button = tk.Button(button_frame, text = "Request IP Address", font = ("Arial", 12), width = 20, bg = GREEN_COLOR, fg = "white", activebackground="#15803D", activeforeground="white", relief = "flat", cursor = "hand2", command = request_ip)
request_button.grid(row = 0, column = 0, padx = 5)

#Release IP button
release_button = tk.Button(button_frame, text = "Release Selected IP", font= ("Arial", 12), width = 20, bg = RED_COLOR, fg = "white", activebackground="#B91C1C", activeforeground="white", relief="flat", cursor="hand2", command = release_selected_ip)
release_button.grid(row = 0, column = 1, padx = 5)

#View configuration button
configuration_button = tk.Button(button_frame, text = "View Client Configuration", width = 23, bg = PURPLE_COLOR, fg = "white", activebackground="#6D28D9", activeforeground="white", relief = "flat", cursor = "hand2", command = show_client_configuration)
configuration_button.grid(row = 0, column = 2, padx = 5)

#Allocated IP table heading
table_label = tk.Label(root, text = "Allocated IP Addresses", font = ("Arial", 14, "bold"), bg=BG_COLOR, fg = "#60A5FA")
table_label.pack(pady=(20, 5))

#Create frame for allocated IP table
table_frame = tk.Frame(root, bg = CARD_COLOR, padx = 10, pady = 10)
table_frame.pack(pady = 10)

#Configure ttk styles
style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview", background="#E2E8F0", foreground="#0F172A", fieldbackground="#E2E8F0", rowheight=32, font=("Arial", 10))

style.configure("Treeview.Heading", background=BLUE_COLOR, foreground="white", font=("Arial", 10, "bold"), relief="flat")

style.map("Treeview", background=[("selected", "#93C5FD")], foreground=[("selected", "#0F172A")])

#Create the table
columns = ("Client ID", "MAC Address", "Assigned IP", "Lease Remaining")

ip_table = ttk.Treeview(table_frame, columns = columns, show = "headings", height = 5)

#Configure column headings
ip_table.heading("Client ID", text="Client ID")
ip_table.heading("MAC Address", text = "MAC Address")
ip_table.heading("Assigned IP", text="Assigned IP")
ip_table.heading("Lease Remaining", text = "Lease Remaining")

#Configure column width
ip_table.column("Client ID", width = 100)
ip_table.column("MAC Address", width = 150)
ip_table.column("Assigned IP", width = 130)
ip_table.column("Lease Remaining", width = 120)

#Place the table inside the frame
ip_table.grid(row = 0, column = 0, padx = 5, pady = 10)

#Create vertical scrollbar
table_scrollbar = tk.Scrollbar(table_frame, orient = "vertical", command = ip_table.yview)
table_scrollbar.grid(row = 0, column = 1, sticky = "ns")

#Connect table to scrollbar
ip_table.config(yscrollcommand=table_scrollbar.set)

#Message log handling
log_label = tk.Label(root, text="DHCP Message Log", font=("Arial", 14, "bold"), bg = BG_COLOR, fg = "#60A5FA")
log_label.pack(pady=(20, 5))

#Message log frame
message_log_frame = tk.Frame(root, bg = CARD_COLOR, padx = 10, pady = 10)
message_log_frame.pack(pady = 10)

#Message log text box
message_log = tk.Text(message_log_frame, height = 8, width = 70, state = "disabled", wrap = "word", bg = LOG_COLOR, fg = "#4ADE80", insertbackground="white", relief = "flat")
message_log.grid(row = 0, column = 0)

#Message log scrollbar
message_scrollbar = tk.Scrollbar(message_log_frame, orient = "vertical", command = message_log.yview)
message_scrollbar.grid(row = 0, column = 1, sticky = "ns")

#Connect text box to scrollbar
message_log.config(yscrollcommand = message_scrollbar.set)

clear_log_button = tk.Button(root, text = "Clear Message Log", font = ("Arial", 10, "bold"), bg = "#475569", fg = "white", activebackground="#64748B", activeforeground="white", relief="flat", cursor = "hand2", command = clear_message_log)
clear_log_button.pack(pady=(0, 15))

#Start automatic lease checking
root.after(1000, update_leases)

#Start GUI Event loop
root.mainloop()