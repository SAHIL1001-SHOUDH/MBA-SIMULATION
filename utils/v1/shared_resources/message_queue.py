from queue import Queue
import threading

class MessageQueue:
    def __init__(self):
        self.queue = Queue()
        self.new_message_event = threading.Event()
    
    def send_message(self, message):
        self.queue.put(message)
        self.new_message_event.set()
    
    def get_messages(self):
        messages = []
        while not self.queue.empty():
            messages.append(self.queue.get())
        self.new_message_event.clear()
        return messages

message_queue = MessageQueue()

def send_message(message):
    message_queue.send_message(message)