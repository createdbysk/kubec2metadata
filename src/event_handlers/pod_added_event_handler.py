import pods
import logging

logger = logging.getLogger(__name__)

class PodAddedEventHandler(object):
    def __init__(self):
        self.__pods = pods.Pods()

    def handle(self, pod):
        logger.info("Handle the pod ADDED event.")
        pod_role = self.__pods.get_pod_role(pod)
        if not pod_role:
            logger.info("Pod does not have a pod role.")
            return

        logger.info(f"Pod has pod role {pod_role}.")
        self.__pods.ensure_ec2_metadata(pod)
        logger.info("Handled the pod ADDED event.")
