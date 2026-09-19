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

        # ==========================================
        # DHCP Clients
        # ==========================================

        self.clients = {}

        client_a = DHCPClient("Client A")

        self.clients["Client A"] = client_a

        # Keep this temporarily for compatibility
        # with the existing DHCP flow.
        self.client = client_a

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

        self.selected_device = None

        self.packet = None

        self.positions = {
            "switch": (430, 210),
            "relay": (650, 210),
            "server": (870, 210)
        }

        self.client_positions = {}

        self.create_widgets()

        # ==========================================
    # Client Management
    # ==========================================

    def add_client(self):

        client_number = len(self.clients) + 1

        client_id = f"Client {chr(64 + client_number)}"

        client = DHCPClient(client_id)

        self.clients[client_id] = client

        # Redraw topology so the new client appears
        self.draw_topology()

        self.add_log(
            f"[CLIENT] {client_id} added to network."
        )

        return client
    
    # ==========================================
    # GUI
    # ==========================================

    def create_widgets(self):

        # ==========================================
        # Main window styling
        # ==========================================

        self.root.configure(bg="#f4f6f8")

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold"),
            background="#1f2937",
            foreground="white"
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
            background="#1f2937",
            foreground="#d1d5db"
        )

        style.configure(
            "Panel.TLabelframe",
            background="#ffffff"
        )

        style.configure(
            "Panel.TLabelframe.Label",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "Control.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8)
        )

        # ==========================================
        # Header
        # ==========================================

        header = tk.Frame(
            self.root,
            bg="#1f2937",
            height=75
        )

        header.pack(
            fill="x",
            side="top"
        )

        header.pack_propagate(False)

        title_frame = tk.Frame(
            header,
            bg="#1f2937"
        )

        title_frame.pack(
            side="left",
            padx=25,
            pady=10
        )

        tk.Label(
            title_frame,
            text="DHCP NETWORK SIMULATOR",
            font=("Segoe UI", 21, "bold"),
            bg="#1f2937",
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Visualize DHCP allocation, leases, renewal and network communication",
            font=("Segoe UI", 9),
            bg="#1f2937",
            fg="#cbd5e1"
        ).pack(anchor="w")

        # Simulation status

        status_frame = tk.Frame(
            header,
            bg="#1f2937"
        )

        status_frame.pack(
            side="right",
            padx=25
        )

        self.status_indicator = tk.Label(
            status_frame,
            text="● READY",
            font=("Segoe UI", 11, "bold"),
            bg="#1f2937",
            fg="#22c55e"
        )

        self.status_indicator.pack()

        # ==========================================
        # Main content area
        # ==========================================

        main_frame = tk.Frame(
            self.root,
            bg="#f4f6f8"
        )

        main_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        # ==========================================
        # Left sidebar
        # ==========================================

        sidebar = tk.Frame(
            main_frame,
            bg="white",
            width=210,
            bd=1,
            relief="solid"
        )

        sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="DEVICES",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#374151"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.device_list_frame = tk.Frame(
            sidebar,
            bg="white"
        )

        self.device_list_frame.pack(
            fill="both",
            expand=True,
            padx=10
        )

        # Client

        self.create_device_list_item(
            "client",
            "●  Client A",
            "DHCP Client"
        )

        # Switch

        self.create_device_list_item(
            "switch",
            "◆  Switch 1",
            "Layer 2 Switch"
        )

        # Relay

        self.create_device_list_item(
            "relay",
            "↔  Relay R1",
            "DHCP Relay"
        )

        # Server

        self.create_device_list_item(
            "server",
            "■  Server S1",
            "DHCP Server"
        )

        # ==========================================
        # Center area
        # ==========================================

        center_frame = tk.Frame(
            main_frame,
            bg="#f4f6f8"
        )

        center_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ------------------------------------------
        # Topology panel
        # ------------------------------------------

        topology_frame = ttk.LabelFrame(
            center_frame,
            text="Network Topology",
            style="Panel.TLabelframe"
        )

        topology_frame.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            topology_frame,
            bg="#f8fafc",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # ==========================================
        # Bottom controls
        # ==========================================

        controls = tk.Frame(
            center_frame,
            bg="#f4f6f8"
        )

        controls.pack(
            fill="x",
            pady=(10, 0)
        )

        self.start_button = tk.Button(
            controls,
            text="▶  Start DHCP",
            command=self.start_dhcp,
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2"
        )

        self.start_button.pack(
            side="left",
            padx=(0, 8)
        )

        tk.Button(
            controls,
            text="↻  Reset",
            command=self.reset,
            font=("Segoe UI", 10, "bold"),
            bg="#e5e7eb",
            fg="#374151",
            activebackground="#d1d5db",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2"
        ).pack(
            side="left"
        )

        # Future buttons

        self.add_client_button = tk.Button(
            controls,
            text="+ Client",
            command=self.add_client,
            font=("Segoe UI", 10),
            bg="white",
            fg="#374151",
            activebackground="#e5e7eb",
            relief="solid",
            bd=1,
            padx=14,
            pady=7,
            cursor="hand2"
        )

        self.add_client_button.pack(
            side="right",
            padx=4
        )

        tk.Button(
            controls,
            text="+ Server",
            font=("Segoe UI", 10),
            bg="white",
            fg="#374151",
            relief="solid",
            bd=1,
            padx=14,
            pady=7,
            state="disabled"
        ).pack(
            side="right",
            padx=4
        )

        # ==========================================
        # Right information panel
        # ==========================================

        right_panel = tk.Frame(
            main_frame,
            bg="#f4f6f8",
            width=270
        )

        right_panel.pack(
            side="right",
            fill="y",
            padx=(12, 0)
        )

        right_panel.pack_propagate(False)

        # ------------------------------------------
        # Device information
        # ------------------------------------------

        info_frame = ttk.LabelFrame(
            right_panel,
            text="Device Information",
            style="Panel.TLabelframe"
        )

        info_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.info_label = tk.Label(
            info_frame,
            text="Select a device\n\nto view information.",
            font=("Segoe UI", 9),
            bg="white",
            fg="#4b5563",
            justify="left",
            anchor="nw"
        )

        self.info_label.pack(
            fill="x",
            padx=12,
            pady=12
        )

        # ------------------------------------------
        # Current DHCP state
        # ------------------------------------------

        state_frame = ttk.LabelFrame(
            right_panel,
            text="DHCP State",
            style="Panel.TLabelframe"
        )

        state_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.state_label = tk.Label(
            state_frame,
            text="INIT",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#6b7280"
        )

        self.state_label.pack(
            pady=15
        )

        # ------------------------------------------
        # Lease information
        # ------------------------------------------

        lease_frame = ttk.LabelFrame(
            right_panel,
            text="Lease",
            style="Panel.TLabelframe"
        )

        lease_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.lease_label = tk.Label(
            lease_frame,
            text="No active lease",
            font=("Segoe UI", 9),
            bg="white",
            fg="#4b5563",
            justify="left"
        )

        self.lease_label.pack(
            anchor="w",
            padx=12,
            pady=12
        )

        # ==========================================
        # Event log
        # ==========================================

        log_frame = ttk.LabelFrame(
            self.root,
            text="Event Log",
            style="Panel.TLabelframe"
        )

        log_frame.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        self.log = tk.Text(
            log_frame,
            height=7,
            font=("Consolas", 9),
            bg="#111827",
            fg="#e5e7eb",
            insertbackground="white",
            relief="flat",
            state="disabled"
        )

        self.log.pack(
            fill="x",
            padx=6,
            pady=6
        )

        # ==========================================
        # Initial state
        # ==========================================

        self.draw_topology()

        self.root.after(
            1000,
            self.update_client_info
        )

        self.add_log(
            "[INFO] Simulator ready."
        )

        self.add_log(
            "[INFO] Select a device to view its information."
        )


    def create_device_list_item(
        self,
        device_id,
        title,
        subtitle
    ):

        frame = tk.Frame(
            self.device_list_frame,
            bg="white",
            cursor="hand2"
        )

        frame.pack(
            fill="x",
            pady=4
        )

        title_label = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1f2937",
            anchor="w"
        )

        title_label.pack(
            fill="x",
            padx=8,
            pady=(6, 0)
        )

        subtitle_label = tk.Label(
            frame,
            text=subtitle,
            font=("Segoe UI", 8),
            bg="white",
            fg="#6b7280",
            anchor="w"
        )

        subtitle_label.pack(
            fill="x",
            padx=8,
            pady=(0, 6)
        )

        def select_device(event=None):
            self.show_device_info(device_id)

        frame.bind(
            "<Button-1>",
            select_device
        )

        title_label.bind(
            "<Button-1>",
            select_device
        )

        subtitle_label.bind(
            "<Button-1>",
            select_device
        )

    # ==========================================
    # Calculate Client Positions
    # ==========================================

    def calculate_client_positions(self):

        self.client_positions = {}

        client_ids = list(self.clients.keys())

        if not client_ids:
            return

        # Maximum number of clients per column
        max_per_column = 4

        start_x = 100
        start_y = 120
        vertical_spacing = 80

        for index, client_id in enumerate(client_ids):

            column = index // max_per_column
            row = index % max_per_column

            x = start_x + (column * 120)
            y = start_y + (row * vertical_spacing)

            self.client_positions[client_id] = (
                x,
                y
            )

    # ==========================================
    # Topology
    # ==========================================

    def draw_topology(self):

        self.canvas.delete("all")

        self.device_shapes = {}

        # Calculate client positions
        self.calculate_client_positions()

        positions = self.positions

        # ==========================================
        # Network labels
        # ==========================================

        self.canvas.create_text(
            270,
            45,
            text="CLIENT NETWORK",
            font=("Segoe UI", 10, "bold"),
            fill="#64748b"
        )

        self.canvas.create_text(
            780,
            45,
            text="SERVER NETWORK",
            font=("Segoe UI", 10, "bold"),
            fill="#64748b"
        )

        self.canvas.create_text(
            270,
            68,
            text="192.168.2.0/24",
            font=("Consolas", 9),
            fill="#94a3b8"
        )

        self.canvas.create_text(
            780,
            68,
            text="192.168.1.0/24",
            font=("Consolas", 9),
            fill="#94a3b8"
        )

        # ==========================================
        # Subnet boundary
        # ==========================================

        self.canvas.create_line(
            770,
            90,
            770,
            430,
            fill="#cbd5e1",
            dash=(5, 5),
            width=2
        )

        self.canvas.create_text(
            770,
            250,
            text="SUBNET\nBOUNDARY",
            font=("Segoe UI", 8),
            fill="#94a3b8"
        )

        # ==========================================
        # Client → Switch connections
        # ==========================================

        switch_x, switch_y = positions["switch"]

        for client_id, (client_x, client_y) in self.client_positions.items():

            self.canvas.create_line(
                client_x + 65,
                client_y,
                switch_x - 65,
                switch_y,
                fill="#94a3b8",
                width=2
            )

        # ==========================================
        # Switch → Relay
        # ==========================================

        self.canvas.create_line(
            switch_x + 65,
            switch_y,
            positions["relay"][0] - 65,
            positions["relay"][1],
            fill="#94a3b8",
            width=3
        )

        # ==========================================
        # Relay → Server
        # ==========================================

        self.canvas.create_line(
            positions["relay"][0] + 65,
            positions["relay"][1],
            positions["server"][0] - 65,
            positions["server"][1],
            fill="#94a3b8",
            width=3
        )

        # ==========================================
        # Draw clients
        # ==========================================

        for client_id, (x, y) in self.client_positions.items():

            self.draw_client_device(
                client_id,
                x,
                y
            )

        # ==========================================
        # Draw fixed devices
        # ==========================================

        for device_id in [
            "switch",
            "relay",
            "server"
        ]:

            position = positions[device_id]

            device = self.devices[device_id]

            self.draw_device(
                device_id,
                position[0],
                position[1],
                device["name"],
                device["type"]
            )

    # ==========================================
    # Draw Client
    # ==========================================

    def draw_client_device(
        self,
        client_id,
        x,
        y
    ):

        width = 110
        height = 65

        rectangle = self.canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x + width // 2,
            y + height // 2,
            outline="#cbd5e1",
            width=2,
            fill="white"
        )

        # Blue accent

        self.canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x - width // 2 + 6,
            y + height // 2,
            outline="#2563eb",
            fill="#2563eb"
        )

        # Client icon

        self.canvas.create_text(
            x,
            y - 16,
            text="▣",
            font=("Segoe UI", 16, "bold"),
            fill="#2563eb"
        )

        # Client name

        self.canvas.create_text(
            x,
            y + 5,
            text=client_id,
            font=("Segoe UI", 9, "bold"),
            fill="#1f2937"
        )

        # State

        client = self.clients[client_id]

        state = client.state.value

        self.canvas.create_text(
            x,
            y + 22,
            text=state,
            font=("Segoe UI", 7),
            fill="#6b7280"
        )

        # Store shape

        self.device_shapes[
            client_id
        ] = rectangle

        # Click

        self.canvas.tag_bind(
            rectangle,
            "<Button-1>",
            lambda event, c=client_id:
            self.show_client_info(c)
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

        width = 130
        height = 85

        # ==========================================
        # Device colors
        # ==========================================

        device_colors = {
            "client": "#2563eb",
            "switch": "#7c3aed",
            "relay": "#ea580c",
            "server": "#16a34a"
        }

        accent = device_colors.get(
            device_id,
            "#64748b"
        )

        # ==========================================
        # Device body
        # ==========================================

        rectangle = self.canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x + width // 2,
            y + height // 2,
            outline="#cbd5e1",
            width=2,
            fill="white",
            tags=("device", device_id)
        )

        # ==========================================
        # Accent bar
        # ==========================================

        self.canvas.create_rectangle(
            x - width // 2,
            y - height // 2,
            x - width // 2 + 7,
            y + height // 2,
            outline=accent,
            fill=accent,
            tags=("device", device_id)
        )

        # ==========================================
        # Device icon
        # ==========================================

        icons = {
            "client": "▣",
            "switch": "◆",
            "relay": "↔",
            "server": "▤"
        }

        self.canvas.create_text(
            x,
            y - 23,
            text=icons.get(device_id, "●"),
            font=("Segoe UI", 18, "bold"),
            fill=accent,
            tags=("device", device_id)
        )

        # ==========================================
        # Name
        # ==========================================

        self.canvas.create_text(
            x,
            y + 2,
            text=name,
            font=("Segoe UI", 10, "bold"),
            fill="#1f2937",
            tags=("device", device_id)
        )

        # ==========================================
        # Type
        # ==========================================

        self.canvas.create_text(
            x,
            y + 21,
            text=device_type,
            font=("Segoe UI", 8),
            fill="#6b7280",
            tags=("device", device_id)
        )

        self.device_shapes[device_id] = rectangle

        # ==========================================
        # Click handling
        # ==========================================

        self.canvas.tag_bind(
            rectangle,
            "<Button-1>",
            lambda event, d=device_id:
            self.show_device_info(d)
        )

        self.canvas.tag_bind(
            device_id,
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

        # ==========================================
    # Client Information
    # ==========================================

    def show_client_info(self, client_id):

        self.selected_device = client_id

        client = self.clients[client_id]

        if client.ip_address:
            ip = client.ip_address
        else:
            ip = "0.0.0.0"

        if client.mac_address:
            mac = client.mac_address
        else:
            mac = "Not assigned"

        remaining = client.get_remaining_lease_time()

        if remaining is not None:
            lease = f"{remaining:.1f} seconds"
        else:
            lease = "No active lease"

        info = (
            f"{client_id}\n"
            f"Type: DHCP Client\n"
            f"State: {client.state.value}\n"
            f"IP Address: {ip}\n"
            f"MAC Address: {mac}\n"
            f"Network: 192.168.2.0/24\n"
            f"Lease Remaining: {lease}"
        )

        self.info_label.config(
            text=info
        )

        self.state_label.config(
            text=client.state.value
        )

        self.lease_label.config(
            text=(
                f"IP Address: {ip}\n"
                f"Remaining: {lease}"
            )
        )

        self.add_log(
            f"[DEVICE] {client_id} selected."
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

        # ==========================================
        # Update dashboard state
        # ==========================================

        self.state_label.config(
            text=new_state.value
        )

        state_colors = {
            "INIT": "#6b7280",
            "SELECTING": "#2563eb",
            "REQUESTING": "#f59e0b",
            "BOUND": "#16a34a",
            "RENEWING": "#ea580c",
            "REBINDING": "#dc2626"
        }

        self.state_label.config(
            fg=state_colors.get(
                new_state.value,
                "#6b7280"
            )
        )

        self.lease_label.config(
            text=(
                f"IP Address: {ip}\n"
                f"Remaining: {lease}"
            )
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

    def send_discover(self, client_id="Client A"):

        client = self.clients.get(client_id)

        if client is None:
            self.add_log(
                f"[ERROR] Client {client_id} not found."
            )
            return

        client.state = self.client.state.INIT

        if client.mac_address is None:
            mac = self.server.get_mac_address(
                client.client_id
            )

            client.assign_mac(mac)

        self.devices["client"]["mac"] = client.mac_address

        discover = DHCPMessage(
            message_type=DHCPMessageType.DISCOVER,
            source=client.client_id,
            destination="255.255.255.255",
            client_id=client.client_id,
            client_mac=client.mac_address
        )

        self.add_log(
            f"[DHCPDISCOVER] {client_id} → Switch → Relay R1"
        )

        self.add_log(
            f"    MAC: {client.mac_address}"
        )

        self.highlight_device("client")

        client_position = self.client_positions.get(
            client_id
        )

        if client_position is None:
            self.add_log(
                f"[ERROR] No topology position for {client_id}."
            )
            return

        self.highlight_device(client_id)

        self.animate_packet(
            client_position,
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
    # =========================================

    def receive_ack(self, ack):

        self.highlight_device("server")

        if ack.message_type == DHCPMessageType.ACK:

            self.add_log(
                f"[DHCPACK] S1 → Relay R1 → "
                f"{ack.client_id}"
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
                f"[DHCPNAK] "
                f"{ack.client_id} request rejected."
            )

            self.start_button.config(
                state="normal"
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

        self.highlight_device(
            offer.client_id
        )

        client_position = self.client_positions.get(
            offer.client_id
        )

        if client_position is None:

            self.add_log(
                f"[ERROR] No topology position for "
                f"{offer.client_id}."
            )

            return

        self.animate_packet(
            self.positions["switch"],
            client_position,
            "DHCPOFFER",
            callback=lambda: self.send_request(
                offer.client_id
            )
        )

    # ==========================================
    # DHCPREQUEST
    # ==========================================

    def send_request(self, client_id="Client A"):

        client = self.clients.get(client_id)

        if client is None:
            self.add_log(
                f"[ERROR] Client {client_id} not found."
            )
            return

        selected_offer = client.choose_best_offer()

        if selected_offer is None:

            self.add_log(
                f"[ERROR] {client_id} has no valid DHCP offer."
            )

            self.start_button.config(
                state="normal"
            )

            return

        request = DHCPMessage(
            message_type=DHCPMessageType.REQUEST,
            source=client.client_id,
            destination=selected_offer.source,
            client_id=client.client_id,
            client_mac=client.mac_address,
            offered_ip=selected_offer.offered_ip
        )

        self.highlight_device(
            client_id
        )

        self.add_log(
            f"[DHCPREQUEST] "
            f"{client_id} → Relay R1 → S1"
        )

        self.add_log(
            f"    Requested IP: "
            f"{selected_offer.offered_ip}"
        )

        client_position = self.client_positions.get(
            client_id
        )

        if client_position is None:

            self.add_log(
                f"[ERROR] No topology position for "
                f"{client_id}."
            )

            return

        self.animate_packet(
            client_position,
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

        self.highlight_device(
            ack.client_id
        )

        client_position = self.client_positions.get(
            ack.client_id
        )

        if client_position is None:

            self.add_log(
                f"[ERROR] No topology position for "
                f"{ack.client_id}."
            )

            return

        self.animate_packet(
            self.positions["switch"],
            client_position,
            "DHCPACK",
            callback=lambda: self.complete_ack(
                ack
            )
        )

    def complete_ack(self, ack):

        client = self.clients.get(
            ack.client_id
        )

        if client is None:

            self.add_log(
                f"[ERROR] Client {ack.client_id} not found."
            )

            return

        self.highlight_device(
            ack.client_id
        )

        if ack.message_type == DHCPMessageType.ACK:

            client.receive_ack(
                ack.offered_ip,
                lease_duration=self.server.lease_duration
            )

            self.add_log(
                f"[SUCCESS] {ack.client_id} received DHCPACK."
            )

            self.add_log(
                f"[IP ASSIGNED] "
                f"{ack.client_id} → "
                f"{client.ip_address}"
            )

            self.finish_dhcp(
                ack.client_id
            )

        else:

            self.add_log(
                f"[DHCPNAK] "
                f"{ack.client_id} request rejected."
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

        # Reset all device outlines

        for shape_id in self.device_shapes.values():

            self.canvas.itemconfig(
                shape_id,
                outline="#cbd5e1",
                width=2
            )

        # Highlight selected/active device

        shape = self.device_shapes.get(
            device_id
        )

        if shape:

            self.canvas.itemconfig(
                shape,
                outline="#2563eb",
                width=4
            )

        # Update sidebar selection visually

        if hasattr(self, "device_list_frame"):

            for widget in self.device_list_frame.winfo_children():

                widget.configure(
                    bg="white"
                )

                for child in widget.winfo_children():

                    child.configure(
                        bg="white"
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