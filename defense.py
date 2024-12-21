import can
import time
import threading

# Configuration
CAN_INTERFACE = 'can0'  # Change to your CAN interface
BUS_TYPE = 'socketcan'   # Adjust based on your platform
BITRATE = 500000         # CAN bus bitrate
SPOOFED_IDS = {0x00F, 0x200}  # Spoofed IDs to monitor
DETECTION_THRESHOLD = 1       # Threshold for detection
DETECTION_INTERVAL = 2        # Time interval for counting messages

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

def send_defensive_message(bus, arbitration_id, dlc, is_extended_id):
    # Create defensive message
    defensive_message = can.Message(
        arbitration_id=arbitration_id,
        data=[0x00] * dlc,
        is_extended_id=is_extended_id
    )
    try:
        bus.send(defensive_message)
        print(f"Sent defensive message: ID={hex(defensive_message.arbitration_id)}")
    except can.CanError as e:
        print(f"Error sending defensive message: {e}")

def execute_defense(bus, spoofed_message):
    # Parrot defense logic
    collisions_detected = 0

    # Phase 1: Cause 16 collisions to push attacker into error-passive state
    while collisions_detected < 16:
        send_defensive_message(
            bus,
            spoofed_message.arbitration_id,
            spoofed_message.dlc,
            spoofed_message.is_extended_id
        )
        time.sleep(0.00032)  # 320 µs delay
        collisions_detected += 1

    print("Collision phase completed. Attacker in error-passive state.")

    # Phase 2: Send 15 more defensive messages to push attacker into bus-off
    for _ in range(15):
        send_defensive_message(
            bus,
            spoofed_message.arbitration_id,
            spoofed_message.dlc,
            spoofed_message.is_extended_id
        )
        time.sleep(0.00032)  # 320 µs delay

    print("Bus-off phase completed. Attacker neutralized.")

def main():
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
                print(f"Received message: ID={hex(message.arbitration_id)}")
                if detector.is_spoofed(message):
                    print(f"Spoofed message detected: ID={hex(message.arbitration_id)}")
                    execute_defense(bus, message)
            else:
                continue
    except KeyboardInterrupt:
        print("Shutting down.")
    finally:
        notifier.stop()
        bus.shutdown()

if __name__ == "__main__":
    main()
