import heapq

class EventQueue:
    def __init__(self):
        self.events = []
    
    def schedule_event(self, timestamp, event_type, data=None):
        """
        Schedules an event in the Priority Queue.
        Events are tuples of (timestamp, event_type, data)
        """
        heapq.heappush(self.events, (timestamp, event_type, data))
        
    def next_event(self):
        """
        Pulls the chronologically next event from the queue.
        Returns (timestamp, event_type, data) or None if empty.
        """
        if self.events:
            return heapq.heappop(self.events)
        return None
        
    def is_empty(self):
        return len(self.events) == 0
