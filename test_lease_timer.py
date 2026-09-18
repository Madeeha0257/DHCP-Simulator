import time

from dhcp_core import DHCPClient, DHCPClientState


client = DHCPClient("Client A")

print("Initial state:", client.state.value)

client.receive_ack(
    ip_address="192.168.1.100",
    lease_duration=4
)

print("After ACK:", client.state.value)
print("Assigned IP:", client.ip_address)
print("Remaining lease:", client.get_remaining_lease_time(), "seconds")

time.sleep(2.2)

client.update_state_from_timer()

print("After T1:", client.state.value)
print("Remaining lease:", client.get_remaining_lease_time(), "seconds")

time.sleep(1.4)

client.update_state_from_timer()

print("After T2:", client.state.value)
print("Remaining lease:", client.get_remaining_lease_time(), "seconds")

time.sleep(0.8)

client.update_state_from_timer()

print("After expiry:", client.state.value)
print("IP after expiry:", client.ip_address)