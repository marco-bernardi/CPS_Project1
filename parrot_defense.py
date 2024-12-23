import can
import time

# Configuration
CAN_INTERFACE = 'can0'
MY_IDS = [0x00F]  # Replace with your legitimate ECU message IDs
DMESSAGE_DATA = [0x00] * 8  # Defensive message data (all zeros)

# Initialize CAN bus
bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

def send_defensive_message(message_id):
    """Send a defensive CAN message."""
    msg = can.Message(arbitration_id=message_id, data=DMESSAGE_DATA, is_extended_id=False)
    try:
        bus.send(msg)
        print(f"Sent defensive message with ID: {hex(message_id)}")
    except can.CanError as e:
        print(f"Failed to send defensive message. Error: {e}")

def parrot_defense():
    """Parrot defense mechanism."""
    print("Parrot defense system activated")
    while True:
        # Listen for CAN messages
        msg = bus.recv()
        if msg:
            print(f"Received message: ID={hex(msg.arbitration_id)}, Data={msg.data}")
            
            # Check if the message is spoofed (i.e., using MY_IDS)
            if msg.arbitration_id in MY_IDS and msg.data != DMESSAGE_DATA:
                print(f"Detected spoofed message with ID: {hex(msg.arbitration_id)}")
                # Send defensive messages at maximum speed
                for _ in range(3650):
                    send_defensive_message(msg.arbitration_id)

if __name__ == "__main__":
    try:
        parrot_defense()
    except KeyboardInterrupt:
        print("Exiting...")
        bus.shutdown()
