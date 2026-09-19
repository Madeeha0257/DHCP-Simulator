from dhcp_core import DHCPServer, DHCPClient


server1 = DHCPServer(
    server_id="S1",
    server_ip="192.168.1.1",
    ip_pool=[
        "192.168.1.100",
        "192.168.1.101"
    ],
    lease_duration=60
)

server2 = DHCPServer(
    server_id="S2",
    server_ip="192.168.1.2",
    ip_pool=[
        "192.168.1.200",
        "192.168.1.201"
    ],
    lease_duration=60
)


client = DHCPClient("Client A")

print("Client:", client.client_id)
print("Initial state:", client.state.value)

# Both DHCP servers receive DHCPDISCOVER
offer1 = server1.discover(client.client_id)
offer2 = server2.discover(client.client_id)

print("\nOffers received:")
print(
    offer1.source,
    "offered",
    offer1.offered_ip
)

print(
    offer2.source,
    "offered",
    offer2.offered_ip
)

# Client receives both offers
client.receive_offers([offer1, offer2])

print("\nNumber of offers:", len(client.offers))
print("Client state:", client.state.value)

# Client chooses one offer
selected_offer = client.choose_best_offer()

print("\nSelected server:", selected_offer.source)
print("Selected IP:", selected_offer.offered_ip)
print("Client state:", client.state.value)

# Client sends DHCPREQUEST to selected server
if selected_offer.source == server1.server_id:
    ack = server1.request(
        client.client_id,
        selected_offer.offered_ip
    )
else:
    ack = server2.request(
        client.client_id,
        selected_offer.offered_ip
    )

print("\nFinal message:", ack.message_type.value)

if ack.message_type.value == "DHCPACK":
    client.receive_ack(
        ack.offered_ip,
        lease_duration=60
    )

print("Assigned IP:", client.ip_address)
print("Final client state:", client.state.value)

print("\nServer S1 leases:", server1.leases)
print("Server S2 leases:", server2.leases)