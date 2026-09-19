import tkinter as tk
from tkinter import ttk

from dhcp_core import (
    DHCPServer,
    DHCPClient,
    DHCPRelayAgent,
    DHCPMessage,
    DHCPMessageType
)


class DHCPTopologyUI:

    def __init__(self, root):
        self.root = root

        self.root.title("DHCP Simulator")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        # ==========================================
        # DHCP objects
        # ==========================================

        self.server = DHCPServer(
            server_id="S1",
            server_ip="192.168.1.1",
            ip_pool=[
                "192.168.2.100",
                "192.168.2.101"
            ],
            lease_duration=60
        )

        self.client = DHCPClient("Client A")

        self.relay = DHCPRelayAgent(
            relay_id="R1",
            relay_ip="192.168.2.1",
            client_network="192.168.2.0/24",
            server_network="192.168.1.0/24"
        )

        # GUI device information
        self.devices = {
            "client": {
                "name": "CLIENT A",
                "type": "DHCP Client",
                "ip": "0.0.0.0",
                "mac": "Not assigned",
                "network": "192.168.2.0/24"
            },

            "switch": {
                "name": "SWITCH 1",
                "type": "Layer 2 Switch",
                "ip": "N/A",
                "mac": "N/A",
                "network": "192.168.2.0/24"
            },

            "relay": {
                "name": "RELAY R1",
                "type": "DHCP Relay",
                "ip": "192.168.2.1",
                "mac": "AA:BB:CC:DD:EE:02",
                "network": "192.168.2.0/24"
            },

            "server": {
                "name": "SERVER S1",
                "type": "DHCP Server",
                "ip": "192.168.1.1",
                "mac": "AA:BB:CC:DD:EE:03",
                "network": "192.168.1.0/24"
            }
        }

        self.device_shapes = {}

        self.create_widgets()

    # ==========================================
    # GUI
    # ==========================================

    def create_widgets(self):

        title = tk.Label(
            self.root,
            text="DHCP SIMULATOR",
            font=("Arial", 22, "bold")
        )

        title.pack(pady=10)

        self.canvas = tk.Canvas(
            self.root,
            bg="white",
            height=430
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Event log

        log_frame = ttk.LabelFrame(
            self.root,
            text="Event Log"
        )

        log_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.log = tk.Text(
            log_frame,
            height=8,
            state="disabled"
        )

        self.log.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # Buttons

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start DHCP",
            command=self.start_dhcp
        )

        self.start_button.pack(
            side="left",
            padx=10
        )

        ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset
        ).pack(
            side="left",
            padx=10
        )

        self.draw_topology()

        self.add_log("[INFO] Simulator ready.")
        self.add_log(
            "[INFO] Click a device to view its information."
        )

    # ==========================================
    # Topology
    # ==========================================

    def draw_topology(self):

        positions = {
            "client": (130, 180),
            "switch": (380, 180),
            "relay": (650, 180),
            "server": (930, 180)
        }

        # Connections

        self.canvas.create_line(
            190, 180,
            320, 180,
            width=3
        )

        self.canvas.create_line(
            440, 180,
            590, 180,
            width=3
        )

        self.canvas.create_line(
            710, 180,
            870, 180,
            width=3
        )

        # Devices

        for device_id, position in positions.items():

            device = self.devices[device_id]

            self.draw_device(
                device_id,
                position[0],
                position[1],
                device["name"],
                device["type"]
            )

    # ==========================================
    # Device
    # ==========================================

    def draw_device(
        self,
        device_id,
        x,
        y,
        name,
        device_type
    ):

        width = 120
        height = 80

        rectangle = self.canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x + width // 2,
            y + height // 2,
            outline="black",
            width=2,
            fill="white"
        )

        self.canvas.create_text(
            x,
            y - 15,
            text=name,
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            x,
            y + 15,
            text=device_type,
            font=("Arial", 9)
        )

        self.device_shapes[device_id] = rectangle

        self.canvas.tag_bind(
            rectangle,
            "<Button-1>",
            lambda event, d=device_id:
            self.show_device_info(d)
        )

    # ==========================================
    # Device information
    # ==========================================

    def show_device_info(self, device_id):

        device = self.devices[device_id]

        self.add_log(
            f"[DEVICE] {device['name']} selected."
        )

        self.add_log(
            f"    Type: {device['type']}"
        )

        self.add_log(
            f"    IP: {device['ip']}"
        )

        self.add_log(
            f"    MAC: {device['mac']}"
        )

        self.add_log(
            f"    Network: {device['network']}"
        )

    # ==========================================
    # Event log
    # ==========================================

    def add_log(self, message):

        self.log.config(state="normal")

        self.log.insert(
            "end",
            message + "\n"
        )

        self.log.see("end")

        self.log.config(state="disabled")

    # ==========================================
    # Start DHCP
    # ==========================================

    def start_dhcp(self):

        self.start_button.config(state="disabled")

        self.add_log("")
        self.add_log(
            "========== DHCP PROCESS STARTED =========="
        )

        self.root.after(
            500,
            self.send_discover
        )

    # ==========================================
    # DHCPDISCOVER
    # ==========================================

    def send_discover(self):

        self.client.state = self.client.state.INIT

        if self.client.mac_address is None:
            mac = self.server.get_mac_address(
                self.client.client_id
            )

            self.client.assign_mac(mac)

        self.devices["client"]["mac"] = self.client.mac_address

        discover = DHCPMessage(
            message_type=DHCPMessageType.DISCOVER,
            source=self.client.client_id,
            destination="255.255.255.255",
            client_id=self.client.client_id,
            client_mac=self.client.mac_address
        )

        self.add_log(
            "[DHCPDISCOVER] Client A → Switch → Relay R1"
        )

        self.add_log(
            f"    MAC: {self.client.mac_address}"
        )

        self.highlight_device("client")

        self.root.after(
            800,
            lambda: self.forward_discover(discover)
        )

    # ==========================================
    # Relay forwards DISCOVER
    # ==========================================

    def forward_discover(self, discover):

        self.highlight_device("relay")

        self.add_log(
            "[RELAY] R1 forwarding DHCPDISCOVER → S1"
        )

        self.root.after(
            800,
            lambda: self.receive_offer(
                self.relay.forward_discover(
                    discover,
                    self.server
                )
            )
        )

    # ==========================================
    # DHCPOFFER
    # ==========================================

    def receive_offer(self, offer):

        self.highlight_device("server")

        self.add_log(
            f"[DHCPOFFER] S1 → Relay R1 → Client A"
        )

        self.add_log(
            f"    Offered IP: {offer.offered_ip}"
        )

        self.client.receive_offer(offer)

        self.root.after(
            800,
            self.send_request
        )

    # ==========================================
    # DHCPREQUEST
    # ==========================================

    def send_request(self):

        selected_offer = self.client.choose_best_offer()

        if selected_offer is None:
            self.add_log(
                "[ERROR] No valid DHCP offer received."
            )

            self.start_button.config(state="normal")
            return

        request = DHCPMessage(
            message_type=DHCPMessageType.REQUEST,
            source=self.client.client_id,
            destination=selected_offer.source,
            client_id=self.client.client_id,
            client_mac=self.client.mac_address,
            offered_ip=selected_offer.offered_ip
        )

        self.highlight_device("client")

        self.add_log(
            "[DHCPREQUEST] Client A → Relay R1 → S1"
        )

        self.add_log(
            f"    Requested IP: {selected_offer.offered_ip}"
        )

        self.root.after(
            800,
            lambda: self.forward_request(request)
        )

    # ==========================================
    # Relay forwards REQUEST
    # ==========================================

    def forward_request(self, request):

        self.highlight_device("relay")

        self.add_log(
            "[RELAY] R1 forwarding DHCPREQUEST → S1"
        )

        self.root.after(
            800,
            lambda: self.receive_ack(
                self.relay.forward_request(
                    request,
                    self.server
                )
            )
        )

    # ==========================================
    # DHCPACK
    # ==========================================

    def receive_ack(self, ack):

        self.highlight_device("server")

        if ack.message_type == DHCPMessageType.ACK:

            self.add_log(
                "[DHCPACK] S1 → Relay R1 → Client A"
            )

            self.add_log(
                f"    Assigned IP: {ack.offered_ip}"
            )

            self.client.receive_ack(
                ack.offered_ip,
                lease_duration=self.server.lease_duration
            )

            self.devices["client"]["ip"] = (
                self.client.ip_address
            )

            self.root.after(
                800,
                self.finish_dhcp
            )

        else:

            self.add_log(
                "[DHCPNAK] Server rejected request."
            )

            self.start_button.config(
                state="normal"
            )

    # ==========================================
    # Finish
    # ==========================================

    def finish_dhcp(self):

        self.highlight_device("client")

        self.add_log(
            "[SUCCESS] DHCP process completed."
        )

        self.add_log(
            f"[STATE] Client A → {self.client.state.value}"
        )

        self.add_log(
            f"[LEASE] {self.client.ip_address}"
        )

        self.add_log(
            "=========================================="
        )

        self.start_button.config(
            state="normal"
        )

    # ==========================================
    # Highlight device
    # ==========================================

    def highlight_device(self, device_id):

        for shape_id in self.device_shapes.values():
            self.canvas.itemconfig(
                shape_id,
                outline="black",
                width=2
            )

        shape = self.device_shapes.get(device_id)

        if shape:
            self.canvas.itemconfig(
                shape,
                outline="blue",
                width=4
            )

    # ==========================================
    # Reset
    # ==========================================

    def reset(self):

        self.client.reset()

        self.server.leases.clear()
        self.server.available_ips = list(
            self.server.ip_pool
        )
        self.server.pending_offers.clear()

        self.devices["client"]["ip"] = "0.0.0.0"
        self.devices["client"]["mac"] = "Not assigned"

        for shape_id in self.device_shapes.values():
            self.canvas.itemconfig(
                shape_id,
                outline="black",
                width=2
            )

        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        self.add_log("[INFO] Simulator reset.")
        self.add_log("[INFO] Simulator ready.")

        self.start_button.config(
            state="normal"
        )


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = DHCPTopologyUI(root)

    root.mainloop()