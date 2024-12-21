import can
import time
import threading

# Configuration
CAN_INTERFACE = 'can0'  # Change to your CAN interface
BUS_TYPE = 'socketcan'   # Change based on your platform (e.g., 'socketcan', 'pcan', 'kvaser')
BITRATE = 500000         # CAN bus bitrate

# Detection Configuration
SPOOFED_IDS = {0x00F, 0x200}  # Example set of IDs to monitor for spoofing
DETECTION_THRESHOLD = 1       # Number of times an ID is seen within the interval to be considered spoofed
DETECTION_INTERVAL = 2        # Time interval in seconds for counting messages

class SpoofingDetector:
    def __init__(self):
        self.message_counts = {}
        self.lock = threading.Lock()
        self.last_reset_time = time.time()

    def reset_counts(self):
        with self.lock:
            self.message_counts.clear()
            self.last_reset_time = time.time()

    def is_spoofed(self, message):
        current_time = time.time()
        if current_time - self.last_reset_time > DETECTION_INTERVAL:
            self.reset_counts()

        with self.lock:
            count = self.message_counts.get(message.arbitration_id, 0) + 1
            self.message_counts[message.arbitration_id] = count
            if count > DETECTION_THRESHOLD and message.arbitration_id in SPOOFED_IDS:
                return True
        return False

def send_defensive_message(bus, message):
    # Create defensive message with same ID and DLC, data field all zeros
    defensive_message = can.Message(
        arbitration_id=message.arbitration_id,
        data=[0x00] * message.dlc,
        is_extended_id=message.is_extended_id
    )
    try:
        bus.send(defensive_message)
        print(f"Sent defensive message: ID={hex(defensive_message.arbitration_id)} Data={defensive_message.data.hex()}")
    except can.CanError as e:
        print(f"Error sending defensive message: {e}")

def main():
    # Initialize CAN bus
    try:
        bus = can.Bus(interface=BUS_TYPE, channel=CAN_INTERFACE, bitrate=BITRATE)
    except Exception as e:
        print(f"Error initializing CAN bus: {e}")
        return

    detector = SpoofingDetector()
    listener = can.BufferedReader()
    notifier = can.Notifier(bus, [listener])

    print("Starting Parrot defensive system. Press Ctrl+C to exit.")
    try:
        while True:
            message = listener.get_message(timeout=1.0)
            if message is not None:
                print(f"Received message: ID={hex(message.arbitration_id)} Data={message.data.hex()}")
                if detector.is_spoofed(message):
                    print(f"Spoofed message detected: ID={hex(message.arbitration_id)}")
                    for i in range(0,11):
                        send_defensive_message(bus, message)
            else:
                # No message received
                continue
    except KeyboardInterrupt:
        print("Shutting down.")
    finally:
        notifier.stop()
        bus.shutdown()

if __name__ == "__main__":
    main()