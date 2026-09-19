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

        self.packet = None


        self.positions = {
            "client": (130, 180),
            "switch": (380, 180),
            "relay": (650, 180),
            "server": (930, 180)
        }

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

        # Device Information Panel

        info_frame = ttk.LabelFrame(
            self.root,
            text="Device Information"
        )

        info_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.info_label = tk.Label(
            info_frame,
            text="Click a device to view its information.",
            font=("Arial", 10),
            justify="left",
            anchor="w"
        )

        self.info_label.pack(
            fill="x",
            padx=10,
            pady=8
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

        self.selected_device = None

        self.root.after(
            1000,
            self.update_client_info
        )

        self.add_log("[INFO] Simulator ready.")
        self.add_log(
            "[INFO] Click a device to view its information."
        )

    # ==========================================
    # Topology
    # ==========================================

    def draw_topology(self):

        positions = self.positions

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

        self.selected_device = device_id

        device = self.devices[device_id]

        # Client-specific information
        if device_id == "client":

            state = self.client.state.value

            if self.client.ip_address:
                ip = self.client.ip_address
            else:
                ip = "0.0.0.0"

            if self.client.mac_address:
                mac = self.client.mac_address
            else:
                mac = "Not assigned"

            remaining = self.client.get_remaining_lease_time()

            if remaining is not None:
                lease = f"{remaining:.1f} seconds"
            else:
                lease = "No active lease"

            info = (
                f"CLIENT A\n"
                f"Type: DHCP Client\n"
                f"State: {state}\n"
                f"IP Address: {ip}\n"
                f"MAC Address: {mac}\n"
                f"Network: {device['network']}\n"
                f"Lease Remaining: {lease}"
            )

        else:

            info = (
                f"{device['name']}\n"
                f"Type: {device['type']}\n"
                f"IP Address: {device['ip']}\n"
                f"MAC Address: {device['mac']}\n"
                f"Network: {device['network']}"
            )

        self.info_label.config(
            text=info
        )

        self.add_log(
            f"[DEVICE] {device['name']} selected."
        )

    def update_client_info(self):
        """Continuously update Client A information."""

        if not hasattr(self, "info_label"):
            return

        if self.client.ip_address:
            ip = self.client.ip_address
        else:
            ip = "0.0.0.0"

        if self.client.mac_address:
            mac = self.client.mac_address
        else:
            mac = "Not assigned"

        # Update DHCP state based on lease timer
        old_state = self.client.state

        self.client.update_state_from_timer()

        new_state = self.client.state

        if (
            old_state != new_state
            and new_state.value == "RENEWING"
        ):
            self.root.after(
                100,
                self.start_renewal
            )

        # Log state transitions
        if old_state != new_state:
            self.add_log(
                f"[STATE CHANGE] Client A: "
                f"{old_state.value} → {new_state.value}"
            )

        remaining = self.client.get_remaining_lease_time()

        if remaining is not None:
            lease = f"{remaining:.1f} seconds"
        else:
            lease = "No active lease"

        info = (
            f"CLIENT A\n"
            f"Type: DHCP Client\n"
            f"State: {new_state.value}\n"
            f"IP Address: {ip}\n"
            f"MAC Address: {mac}\n"
            f"Network: {self.devices['client']['network']}\n"
            f"Lease Remaining: {lease}"
        )

        # Only update the panel if Client A is currently selected
        if getattr(self, "selected_device", None) == "client":
            self.info_label.config(text=info)

        # Run again after 1 second
        self.root.after(1000, self.update_client_info)
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
    # Animate packet
    # ==========================================

    def animate_packet(
        self,
        start,
        end,
        message,
        callback=None,
        steps=30
    ):
        """
        Animates a DHCP packet from one device
        to another.
        """

        # Remove previous packet
        if self.packet is not None:
            self.canvas.delete(self.packet)

        x1, y1 = start
        x2, y2 = end

        # Create packet
        self.packet = self.canvas.create_oval(
            x1 - 8,
            y1 - 8,
            x1 + 8,
            y1 + 8,
            fill="blue",
            outline="black"
        )

        # Packet label
        label = self.canvas.create_text(
            x1,
            y1 - 20,
            text=message,
            font=("Arial", 9, "bold")
        )

        def move_packet(step):

            if step > steps:

                self.canvas.delete(label)

                if callback:
                    callback()

                return

            progress = step / steps

            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress

            self.canvas.coords(
                self.packet,
                x - 8,
                y - 8,
                x + 8,
                y + 8
            )

            self.canvas.coords(
                label,
                x,
                y - 20
            )

            self.root.after(
                30,
                lambda: move_packet(step + 1)
            )

        move_packet(0)

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

        self.animate_packet(
            self.positions["client"],
            self.positions["switch"],
            "DHCPDISCOVER",
            callback=lambda: self.animate_discover_to_relay(
                discover
            )
        )

    # ==========================================
    # Relay forwards DISCOVER
    # ==========================================

    def forward_discover(self, discover):

        self.highlight_device("relay")

        self.add_log(
            "[RELAY] R1 forwarding DHCPDISCOVER → S1"
        )

        offer = self.relay.forward_discover(
            discover,
            self.server
        )

        self.animate_packet(
            self.positions["relay"],
            self.positions["server"],
            "DHCPDISCOVER",
            callback=lambda: self.receive_offer(
                offer
            )
        )

    # ==========================================
    # Animate DISCOVER from Switch to Relay
    # ==========================================

    def animate_discover_to_relay(self, discover):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["relay"],
            "DHCPDISCOVER",
            callback=lambda: self.forward_discover(
                discover
            )
        )

    # ==========================================
    # DHCPOFFER
    # ==========================================
    def receive_offer(self, offer):

        self.highlight_device("server")

        self.add_log(
            "[DHCPOFFER] S1 → Relay R1 → Client A"
        )

        self.add_log(
            f"    Offered IP: {offer.offered_ip}"
        )

        self.client.receive_offer(offer)

        self.animate_packet(
            self.positions["server"],
            self.positions["relay"],
            "DHCPOFFER",
            callback=lambda: self.animate_offer_to_switch(
                offer
            )
        )

    def animate_offer_to_switch(self, offer):

        self.highlight_device("relay")

        self.animate_packet(
            self.positions["relay"],
            self.positions["switch"],
            "DHCPOFFER",
            callback=lambda: self.animate_offer_to_client(
                offer
            )
        )

    def animate_offer_to_client(self, offer):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["client"],
            "DHCPOFFER",
            callback=self.send_request
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

        self.animate_packet(
            self.positions["client"],
            self.positions["switch"],
            "DHCPREQUEST",
            callback=lambda: self.animate_request_to_relay(
                request
            )
        )

    def animate_request_to_relay(self, request):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["relay"],
            "DHCPREQUEST",
            callback=lambda: self.forward_request(
                request
            )
        )

    def animate_renewal_request_to_relay(self, request):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["relay"],
            "DHCPREQUEST",
            callback=lambda: self.forward_renewal_request(
                request
            )
        )

    # ==========================================
    # Relay forwards REQUEST
    # ==========================================

    def forward_request(self, request):

        self.highlight_device("relay")

        self.add_log(
            "[RELAY] R1 forwarding DHCPREQUEST → S1"
        )

        ack = self.relay.forward_request(
            request,
            self.server
        )

        self.animate_packet(
            self.positions["relay"],
            self.positions["server"],
            "DHCPREQUEST",
            callback=lambda: self.receive_ack(
                ack
            )
        )

    # ==========================================
    # Relay forwards RENEWAL REQUEST
    # ==========================================

    def forward_renewal_request(self, request):

        self.highlight_device("relay")

        self.add_log(
            "[RELAY] R1 forwarding renewal REQUEST → S1"
        )

        ack = self.relay.forward_request(
            request,
            self.server
        )

        self.animate_packet(
            self.positions["relay"],
            self.positions["server"],
            "DHCPREQUEST",
            callback=lambda: self.receive_renewal_ack(
                ack
            )
        )

    def receive_renewal_ack(self, ack):

        self.highlight_device("server")

        if ack.message_type == DHCPMessageType.ACK:

            self.add_log(
                "[DHCPACK] S1 → Relay R1 → Client A"
            )

            self.add_log(
                "[RENEWAL SUCCESS] Lease renewed."
            )

            self.animate_packet(
                self.positions["server"],
                self.positions["relay"],
                "DHCPACK",
                callback=lambda: self.animate_renewal_ack_to_switch(
                    ack
                )
            )

        else:

            self.add_log(
                "[DHCPNAK] Renewal rejected."
            )

    def animate_renewal_ack_to_switch(self, ack):

        self.highlight_device("relay")

        self.animate_packet(
            self.positions["relay"],
            self.positions["switch"],
            "DHCPACK",
            callback=lambda: self.animate_renewal_ack_to_client(
                ack
            )
        )


    def animate_renewal_ack_to_client(self, ack):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["client"],
            "DHCPACK",
            callback=lambda: self.complete_renewal(
                ack
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

            self.animate_packet(
                self.positions["server"],
                self.positions["relay"],
                "DHCPACK",
                callback=lambda: self.animate_ack_to_switch(
                    ack
                )
            )

        else:

            self.add_log(
                "[DHCPNAK] Server rejected request."
            )

            self.start_button.config(
                state="normal"
            )

    def animate_ack_to_switch(self, ack):

        self.highlight_device("relay")

        self.animate_packet(
            self.positions["relay"],
            self.positions["switch"],
            "DHCPACK",
            callback=lambda: self.animate_ack_to_client(
                ack
            )
        )

    def animate_ack_to_client(self, ack):

        self.highlight_device("switch")

        self.animate_packet(
            self.positions["switch"],
            self.positions["client"],
            "DHCPACK",
            callback=lambda: self.complete_ack(
                ack
            )
        )

    def complete_ack(self, ack):

        self.highlight_device("client")

        self.client.receive_ack(
            ack.offered_ip,
            lease_duration=self.server.lease_duration
        )

        self.devices["client"]["ip"] = (
            self.client.ip_address
        )

        self.finish_dhcp()

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

    def start_renewal(self):
        """Start DHCP lease renewal."""

        if self.client.ip_address is None:
            return

        self.add_log("")
        self.add_log("========== DHCP RENEWAL ==========")

        self.add_log(
            "[RENEWING] Client A lease reached T1."
        )

        self.add_log(
            "[DHCPREQUEST] Client A → Relay R1 → S1"
        )

        request = DHCPMessage(
            message_type=DHCPMessageType.REQUEST,
            source=self.client.client_id,
            destination=self.server.server_id,
            client_id=self.client.client_id,
            client_mac=self.client.mac_address,
            offered_ip=self.client.ip_address
        )

        self.highlight_device("client")

        self.animate_packet(
            self.positions["client"],
            self.positions["switch"],
            "DHCPREQUEST",
            callback=lambda: self.animate_renewal_request_to_relay(
                request
            )
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


    def complete_renewal(self, ack):

        self.highlight_device("client")

        if ack.message_type == DHCPMessageType.ACK:

            self.client.receive_ack(
                ack.offered_ip,
                lease_duration=self.server.lease_duration
            )

            self.devices["client"]["ip"] = (
                self.client.ip_address
            )

            self.add_log(
                "[SUCCESS] Client A returned to BOUND."
            )

            self.add_log(
                f"[LEASE] New lease: "
                f"{self.server.lease_duration} seconds"
            )

# ==========================================
# Run
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = DHCPTopologyUI(root)

    root.mainloop()