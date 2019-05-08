from .pod_with_role_added_event_handler import *
from .pod_event_handler_chain import *

event_handler_classes = {
    "ADDED": PodWithRoleAddedEventHandler
}

def create_event_handler(event):
    event_handler_class = event_handler_classes[event]
    event_handler = event_handler_class()
    return event_handler
