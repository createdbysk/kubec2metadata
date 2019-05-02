import pods

class PodAddedEventHandler(object):
    def __init__(self):
        self.__pods = pods.Pods()

    def handle(self, pod):
        pod_role = self.__pods.get_pod_role(pod)
        if not pod_role:
            return

        self.__pods.ensure_ec2_metadata(pod)
