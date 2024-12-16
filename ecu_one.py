import can
import time
import os
import threading
from can.interface import Bus

my_id = 0XC0FFEE
spamming = True

try:
    can.rc['interface'] = 'socketcan'
    can.rc['channel'] = 'can0'
    can.rc['bitrate'] = 500000
    bus = Bus()
except OSError:
    print('Cannot find PiCAN board.')
    exit()
    
def send_one():
    """Sends a single message."""
    # this uses the default configuration (for example from the config file)
    # see https://python-can.readthedocs.io/en/stable/configuration.html
    while spamming: 
        with can.Bus() as bus:
            msg = can.Message(
                arbitration_id=0xC0FFEE, data=[0, 25, 0, 1, 3, 1, 4, 1], is_extended_id=True
            )
            try:
                bus.send(msg)
                print(f"Message sent on {bus.channel_info}")
            except can.CanError:
                print("Message NOT sent")
        # Wait 1 second before sending the next message
        time.sleep(1)
        

    # Close the bus when done
    bus.shutdown()
   

print('Ready') 

def msg_listener(id):
    while True:
        """Listens for messages with a specific ID."""
        with can.Bus() as bus:
            for msg in bus:
                if msg.arbitration_id == id:
                    print("Someone is sending message with my Id!!!")
                    print(msg)
                else:
                    # Message for turn off spamming
                    if msg.arbitration_id == 0x0:
                        if msg.data[0] == 0:
                            spamming = False
                            print('Spamming stopped by: ', msg.arbitration_id)
                            break
        bus.shutdown()
    
    

if __name__ == '__main__':
    ## Use one thread to send messages and another to listen for messages
    
    # Send a message
    t1 = threading.Thread(target=send_one)
    t1.start()
    
    # Listen for a message
    t2 = threading.Thread(target=msg_listener, args=(0xC0FFEE,))
    t2.start()
    
    t1.join()
    t2.join()
    
    print('Done')
    
    
    
    