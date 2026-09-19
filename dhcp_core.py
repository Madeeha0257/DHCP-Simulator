import random
import time
from dataclasses import dataclass
from enum import Enum

class DHCPClientState(Enum):
    INIT = "INIT"
    SELECTING = "SELECTING"
    REQUESTING = "REQUESTING"
    BOUND = "BOUND"
    RENEWING = "RENEWING"
    REBINDING = "REBINDING"

class DHCPMessageType(Enum):
    DISCOVER = "DHCPDISCOVER"
    OFFER = "DHCPOFFER"
    REQUEST = "DHCPREQUEST"
    ACK = "DHCPACK"
    NAK = "DHCPNAK"
    RELEASE = "DHCPRELEASE"


@dataclass
class DHCPMessage:
    message_type: DHCPMessageType
    source: str
    destination: str
    client_id: str
    client_mac: str
    offered_ip: str | None = None
    description: str = ""


@dataclass
class DHCPLease:
    client_id: str
    client_mac: str
    ip_address: str
    server_id: str
    lease_start: float
    lease_duration: int

    @property
    def expiry_time(self):
        return self.lease_start + self.lease_duration

    @property
    def remaining_time(self):
        remaining = int(self.expiry_time - time.time())
        return max(0, remaining)

    @property
    def is_expired(self):
        return self.remaining_time <= 0


class DHCPServer:
    def __init__(
        self,
        server_id="S1",
        server_ip="192.168.1.1",
        subnet_mask="255.255.255.0",
        gateway="192.168.1.1",
        dns_server="8.8.8.8",
        ip_pool=None,
        lease_duration=60
    ):
        self.server_id = server_id
        self.server_ip = server_ip
        self.subnet_mask = subnet_mask
        self.gateway = gateway
        self.dns_server = dns_server
        self.lease_duration = lease_duration

        self.ip_pool = ip_pool or [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.1.103"
        ]

        self.available_ips = list(self.ip_pool)

        self.leases = {}
        self.client_macs = {}
        self.pending_offers = {}

    def generate_mac_address(self):
        mac_parts = []

        for _ in range(6):
            mac_parts.append(f"{random.randint(0, 255):02X}")

        return ":".join(mac_parts)

    def get_mac_address(self, client_id):
        if client_id not in self.client_macs:
            self.client_macs[client_id] = self.generate_mac_address()

        return self.client_macs[client_id]

    def discover(self, client_id):
        """
        Simulates DHCPDISCOVER and creates a pending offer.
        It does not allocate the IP permanently yet.
        """

        client_mac = self.get_mac_address(client_id)

        # Client already has an active lease
        if client_id in self.leases:
            existing_lease = self.leases[client_id]

            return DHCPMessage(
                message_type=DHCPMessageType.OFFER,
                source=self.server_id,
                destination=client_id,
                client_id=client_id,
                client_mac=client_mac,
                offered_ip=existing_lease.ip_address,
                description="Client already has an active lease"
            )

        # No IP addresses available
        if not self.available_ips:
            return DHCPMessage(
                message_type=DHCPMessageType.NAK,
                source=self.server_id,
                destination=client_id,
                client_id=client_id,
                client_mac=client_mac,
                description="No available IP addresses"
            )

        offered_ip = self.available_ips[0]

        # Store offer temporarily
        self.pending_offers[client_id] = offered_ip

        return DHCPMessage(
            message_type=DHCPMessageType.OFFER,
            source=self.server_id,
            destination=client_id,
            client_id=client_id,
            client_mac=client_mac,
            offered_ip=offered_ip,
            description=f"Offering IP address {offered_ip}"
        )

    def request(self, client_id, requested_ip):
        """
        Simulates DHCPREQUEST and DHCPACK.
        """

        client_mac = self.get_mac_address(client_id)

        # Handle renewal of an existing lease
        if client_id in self.leases:
            existing_lease = self.leases[client_id]

            if existing_lease.ip_address == requested_ip:
                existing_lease.lease_start = time.time()

                return DHCPMessage(
                    message_type=DHCPMessageType.ACK,
                    source=self.server_id,
                    destination=client_id,
                    client_id=client_id,
                    client_mac=client_mac,
                    offered_ip=requested_ip,
                    description="Existing lease renewed"
                )

        # Verify that the requested IP was offered
        offered_ip = self.pending_offers.get(client_id)

        if offered_ip != requested_ip:
            return DHCPMessage(
                message_type=DHCPMessageType.NAK,
                source=self.server_id,
                destination=client_id,
                client_id=client_id,
                client_mac=client_mac,
                offered_ip=requested_ip,
                description="Requested IP does not match server offer"
            )

        # Verify that the IP is still available
        if requested_ip not in self.available_ips:
            return DHCPMessage(
                message_type=DHCPMessageType.NAK,
                source=self.server_id,
                destination=client_id,
                client_id=client_id,
                client_mac=client_mac,
                offered_ip=requested_ip,
                description="Requested IP is no longer available"
            )

        # Remove IP from available pool
        self.available_ips.remove(requested_ip)

        # Create lease
        lease = DHCPLease(
            client_id=client_id,
            client_mac=client_mac,
            ip_address=requested_ip,
            server_id=self.server_id,
            lease_start=time.time(),
            lease_duration=self.lease_duration
        )

        self.leases[client_id] = lease

        # Remove temporary offer
        self.pending_offers.pop(client_id, None)

        return DHCPMessage(
            message_type=DHCPMessageType.ACK,
            source=self.server_id,
            destination=client_id,
            client_id=client_id,
            client_mac=client_mac,
            offered_ip=requested_ip,
            description=f"IP address {requested_ip} assigned successfully"
        )

    def release(self, client_id):
        """
        Simulates DHCPRELEASE.
        """

        lease = self.leases.pop(client_id, None)

        if lease is None:
            return None

        if lease.ip_address not in self.available_ips:
            self.available_ips.append(lease.ip_address)

        return DHCPMessage(
            message_type=DHCPMessageType.RELEASE,
            source=client_id,
            destination=self.server_id,
            client_id=client_id,
            client_mac=lease.client_mac,
            offered_ip=lease.ip_address,
            description=f"IP address {lease.ip_address} released"
        )

    def check_expired_leases(self):
        """
        Finds and removes expired leases.
        """

        expired_leases = []

        for client_id, lease in list(self.leases.items()):
            if lease.is_expired:
                expired_leases.append(lease)

                self.leases.pop(client_id)

                if lease.ip_address not in self.available_ips:
                    self.available_ips.append(lease.ip_address)

        return expired_leases

    def get_lease(self, client_id):
        return self.leases.get(client_id)

class DHCPRelayAgent:
    def __init__(
        self,
        relay_id,
        relay_ip,
        client_network,
        server_network
    ):
        self.relay_id = relay_id
        self.relay_ip = relay_ip
        self.client_network = client_network
        self.server_network = server_network

    def forward_discover(self, message, server):
        """
        Forwards a DHCPDISCOVER from the client
        to the DHCP server.
        """

        print(
            f"[Relay {self.relay_id}] "
            f"Forwarding DHCPDISCOVER "
            f"from {message.client_id} "
            f"to {server.server_id}"
        )

        return server.discover(message.client_id)

    def forward_request(self, message, server):
        """
        Forwards a DHCPREQUEST from the client
        to the DHCP server.
        """

        print(
            f"[Relay {self.relay_id}] "
            f"Forwarding DHCPREQUEST "
            f"from {message.client_id} "
            f"to {server.server_id}"
        )

        return server.request(
            message.client_id,
            message.offered_ip
        )

    def forward_response(self, message, client):
        """
        Forwards the DHCP server response
        back to the client.
        """

        print(
            f"[Relay {self.relay_id}] "
            f"Forwarding {message.message_type.value} "
            f"from DHCP server "
            f"to {client.client_id}"
        )

        return message

class DHCPClient:
    def __init__(self, client_id, mac_address=None):
        self.client_id = client_id
        self.mac_address = mac_address
        self.ip_address = None
        self.state = DHCPClientState.INIT
        self.selected_server = None
        self.offers = []

        # Lease timer information
        self.lease_start_time = None
        self.lease_duration = None
        self.t1_time = None
        self.t2_time = None

    def assign_mac(self, mac_address):
        self.mac_address = mac_address

    def receive_offer(self, offer):
        self.offers.append(offer)
        self.state = DHCPClientState.SELECTING

    def select_offer(self, offer):
        self.selected_server = offer.source
        self.ip_address = offer.offered_ip
        self.state = DHCPClientState.REQUESTING

    def receive_ack(self, ip_address, lease_duration=60):
        self.ip_address = ip_address
        self.state = DHCPClientState.BOUND

        self.lease_start_time = time.time()
        self.lease_duration = lease_duration

        # T1: 50% of lease duration
        self.t1_time = self.lease_start_time + (lease_duration * 0.5)

        # T2: 87.5% of lease duration
        self.t2_time = self.lease_start_time + (lease_duration * 0.875)

    def reset(self):
        self.ip_address = None
        self.state = DHCPClientState.INIT
        self.selected_server = None
        self.offers.clear()

        self.lease_start_time = None
        self.lease_duration = None
        self.t1_time = None
        self.t2_time = None

    def start_renewing(self):
        """
        Client tries to renew its existing lease
        with the original DHCP server.
        """
        if self.state == DHCPClientState.BOUND:
            self.state = DHCPClientState.RENEWING
            return True

        return False

    def start_rebinding(self):
        """
        Client tries to contact any available DHCP server
        because the original server did not respond.
        """
        if self.state in (
            DHCPClientState.BOUND,
            DHCPClientState.RENEWING
        ):
            self.state = DHCPClientState.REBINDING
            return True

        return False

    def renew_successful(self):
        """
        Renewal succeeded.
        """
        self.state = DHCPClientState.BOUND
        return True

    def renewal_failed(self):
        """
        Renewal failed, so the client enters REBINDING.
        """
        if self.state == DHCPClientState.RENEWING:
            self.state = DHCPClientState.REBINDING
            return True

        return False

    def lease_expired(self):
        """
        The lease expired without successful renewal.
        """
        self.ip_address = None
        self.selected_server = None
        self.lease_start_time = None
        self.lease_duration = None
        self.t1_time = None
        self.t2_time = None
        self.state = DHCPClientState.INIT

        return True

    def get_remaining_lease_time(self):
        """
        Returns the remaining lease time in seconds.
        """
        if self.lease_start_time is None or self.lease_duration is None:
            return 0

        elapsed_time = time.time() - self.lease_start_time
        remaining_time = self.lease_duration - elapsed_time

        return max(0, int(remaining_time))

    def update_state_from_timer(self):
        """
        Automatically updates the client state based
        on T1, T2, and lease expiry.
        """
        if self.lease_start_time is None:
            return self.state

        current_time = time.time()

        if current_time >= self.lease_start_time + self.lease_duration:
            self.lease_expired()

        elif current_time >= self.t2_time:
            self.state = DHCPClientState.REBINDING

        elif current_time >= self.t1_time:
            self.state = DHCPClientState.RENEWING

        return self.state

    def choose_best_offer(self):
        """
        Selects one offer from the available DHCP offers.

        For now, the client chooses the first valid offer.
        Later, we can add server priority and network rules.
        """
        if not self.offers:
            return None

        valid_offers = [
            offer
            for offer in self.offers
            if offer.message_type == DHCPMessageType.OFFER
            and offer.offered_ip is not None
        ]

        if not valid_offers:
            return None

        selected_offer = valid_offers[0]

        self.select_offer(selected_offer)

        return selected_offer

    def receive_offers(self, offers):
        """
        Receives offers from multiple DHCP servers.
        """
        self.offers.clear()

        for offer in offers:
            self.receive_offer(offer)

        return self.offers