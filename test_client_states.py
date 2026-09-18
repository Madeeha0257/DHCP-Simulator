from dhcp_core import DHCPClient, DHCPClientState


client = DHCPClient("Client A")

print("Initial state:", client.state.value)

client.state = DHCPClientState.SELECTING
print("After DISCOVER:", client.state.value)

client.state = DHCPClientState.REQUESTING
print("After REQUEST:", client.state.value)

client.state = DHCPClientState.BOUND
client.ip = "192.168.1.100"

print("After ACK:", client.state.value)
print("Assigned IP:", client.ip)

client.start_renewing()
print("During renewal:", client.state.value)

client.renewal_failed()
print("After renewal failure:", client.state.value)

client.renew_successful()
print("After rebinding success:", client.state.value)

client.lease_expired()
print("After lease expiry:", client.state.value)
print("IP after expiry:", client.ip)