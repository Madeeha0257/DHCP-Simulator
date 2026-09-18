from dhcp_core import DHCPServer, DHCPClient, DHCPMessageType


server = DHCPServer(
    server_id="S1",
    server_ip="192.168.1.1",
    lease_duration=20
)

client = DHCPClient("Client A")

print("Client state:", client.state.value)

# DHCPDISCOVER
offer = server.discover(client.client_id)

print("\nMessage:", offer.message_type.value)
print("Server:", offer.source)
print("Offered IP:", offer.offered_ip)
print("Description:", offer.description)

if offer.message_type == DHCPMessageType.OFFER:
    client.assign_mac(offer.client_mac)
    client.receive_offer(offer)

    print("Client state:", client.state.value)

    # DHCPREQUEST
    client.select_offer(offer)

    print("\nClient selected server:", client.selected_server)
    print("Client state:", client.state.value)

    ack = server.request(
        client.client_id,
        offer.offered_ip
    )

    print("\nMessage:", ack.message_type.value)
    print("Assigned IP:", ack.offered_ip)
    print("Description:", ack.description)

    if ack.message_type == DHCPMessageType.ACK:
        client.receive_ack(ack.offered_ip)

        print("Client state:", client.state.value)

        lease = server.get_lease(client.client_id)

        print("\nLease details:")
        print("Client:", lease.client_id)
        print("MAC:", lease.client_mac)
        print("IP:", lease.ip_address)
        print("Server:", lease.server_id)
        print("Remaining time:", lease.remaining_time, "seconds")