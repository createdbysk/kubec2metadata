class PodEventHandlerChain(object):
    def __init__(self, *pod_event_handlers):
        self.__pod_event_handlers = pod_event_handlers

    def handle(self, pod):
        handled = False
        for event_handler in self.__pod_event_handlers:
            handled = event_handler.handle(pod)
            if handled:
                break
        return handled
            
