import threading

class UserInterjectionControl:
    def __init__(self):
        self.interrupt_event = threading.Event()
        self.user_input = None
        self.interrupt_lock = threading.Lock()
    
    def interrupt(self, user_input):
        with self.interrupt_lock:
            self.user_input = user_input
            self.interrupt_event.set()
    
    def check_for_interruption(self):
        return self.interrupt_event.is_set()
    
    def get_and_clear_interruption(self):
        with self.interrupt_lock:
            user_input = self.user_input
            self.user_input = None
            self.interrupt_event.clear()
            return user_input

interjection_control = UserInterjectionControl()