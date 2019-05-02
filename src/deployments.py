from kubernetes import client
import typing
import logging

logger = logging.getLogger(__name__)

class Deployments(object):
    def __init__(self):
        self.__extensions_v1_beta1 = client.ExtensionsV1beta1Api()

    def get_selected_deployments(self,
                                 label_selector_key: str,
                                 label_selector_value: str) \
         -> typing.Generator[client.ExtensionsV1beta1Deployment, None, None]:
        """
        Gets the deployments that have a label key that matches label_selector_key
        that has a value label_selector_value.

        :param label_selector_key:      -   The key of the label.
        :param label_selector_value:    -   The value for that key.
        :return:                            A generator.
        """
        label_selector = f"{label_selector_key}={label_selector_value}"
        logger.info(f"Generate deployments with label selector {label_selector}")
        deployments_response = \
            self.__extensions_v1_beta1.list_deployment_for_all_namespaces(
                label_selector=label_selector
            )
        while True:
            deployments = deployments_response.items
            for deployment in deployments:
                yield deployment
            _continue = deployments_response.metadata._continue
            if _continue is None:
                break
            deployments_response = \
                self.__extensions_v1_beta1.list_deployment_for_all_namespaces(
                    _continue=_continue,
                    label_selector=label_selector)
