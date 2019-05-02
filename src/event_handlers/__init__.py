from .pod_added_event_handler import *

event_handler_classes = {
    "ADDED": PodAddedEventHandler
}

def create_event_handler(event):
    event_handler_class = event_handler_classes[event]
    event_handler = event_handler_class()
    return event_handler
