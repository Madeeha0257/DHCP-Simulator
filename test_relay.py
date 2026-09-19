from dhcp_core import (
    DHCPServer,
    DHCPClient,
    DHCPRelayAgent,
    DHCPMessage,
    DHCPMessageType
)


# --------------------------------
# Create DHCP server
# --------------------------------

server = DHCPServer(
    server_id="S1",
    server_ip="192.168.1.1",
    ip_pool=[
        "192.168.2.100",
        "192.168.2.101"
    ],
    lease_duration=60
)


# --------------------------------
# Create DHCP relay
# --------------------------------

relay = DHCPRelayAgent(
    relay_id="R1",
    relay_ip="192.168.2.1",
    client_network="192.168.2.0/24",
    server_network="192.168.1.0/24"
)


# --------------------------------
# Create DHCP client
# --------------------------------

client = DHCPClient("Client A")


print("Client state:", client.state.value)


# --------------------------------
# Step 1: Client creates DISCOVER
# --------------------------------

discover = DHCPMessage(
    message_type=DHCPMessageType.DISCOVER,
    source=client.client_id,
    destination="255.255.255.255",
    client_id=client.client_id,
    client_mac=client.mac_address
)

print("\nClient → Relay")
print("Message:", discover.message_type.value)


# --------------------------------
# Step 2: Relay forwards DISCOVER
# --------------------------------

offer = relay.forward_discover(
    discover,
    server
)


# --------------------------------
# Step 3: Relay sends OFFER to client
# --------------------------------

offer = relay.forward_response(
    offer,
    client
)

print("\nRelay → Client")
print("Message:", offer.message_type.value)
print("Offered IP:", offer.offered_ip)


# --------------------------------
# Step 4: Client receives OFFER
# --------------------------------

client.receive_offer(offer)

selected_offer = client.choose_best_offer()

print("\nClient selected:")
print("Server:", selected_offer.source)
print("IP:", selected_offer.offered_ip)
print("Client state:", client.state.value)


# --------------------------------
# Step 5: Client creates REQUEST
# --------------------------------

request = DHCPMessage(
    message_type=DHCPMessageType.REQUEST,
    source=client.client_id,
    destination=selected_offer.source,
    client_id=client.client_id,
    client_mac=client.mac_address,
    offered_ip=selected_offer.offered_ip
)

print("\nClient → Relay")
print("Message:", request.message_type.value)


# --------------------------------
# Step 6: Relay forwards REQUEST
# --------------------------------

ack = relay.forward_request(
    request,
    server
)


# --------------------------------
# Step 7: Relay sends ACK to client
# --------------------------------

ack = relay.forward_response(
    ack,
    client
)


# --------------------------------
# Step 8: Client receives ACK
# --------------------------------

if ack.message_type == DHCPMessageType.ACK:
    client.receive_ack(
        ack.offered_ip,
        lease_duration=server.lease_duration
    )


print("\nFinal result:")
print("Client IP:", client.ip_address)
print("Client state:", client.state.value)
print("Server lease:", server.get_lease(client.client_id))