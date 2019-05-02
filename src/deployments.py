from kubernetes import client
import typing
import logging

logger = logging.getLogger(__name__)

class Deployments(object):
    _EC2_METADATA_FOR_LABEL = "ec2_metadata_for"
    _NAMESPACE = "default"

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

    def ensure_ec2_metadata_deployment(self, pod_role: str) -> None:
        """
        Ensures a metadata deployment exists for the given pod_role.

        :param pod_role:    The pod role to create the metadata deployment for.
        """
        logger.info(f"Check for any prior mock metadata deployments"
                     "for {pod_role}.")
        prior_deployments = self.get_selected_deployments(
            Deployments._EC2_METADATA_FOR_LABEL,
            pod_role
        )
        # Iterate over prior deployments.
        # If this enters the for loop, then at least one deployment exists
        # with the given label value.
        # Do not create a deployment in that case.
        for prior_deployment in prior_deployments:
            logger.info(f"Found deployment for {pod_role}. Nothing more to do.")
            return

        logger.info(f"No prior mock metadata deployments"
                     "found for {pod_role}. Create a new one.")
        self.__extensions_v1_beta1.create_namespaced_deployment(
            namespace=Deployments._NAMESPACE,
            body=self.__get_deployment_body(pod_role)
        )
        logger.info(f"Created mock metadata deployment"
                     "for {pod_role}.")

    def __get_deployment_body(self, pod_role: str) -> str:
        import yaml
        deployment_yaml = f"""
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {pod_role}-mock-metadata
  labels:
    ec2_metadata_for: {pod_role}
spec:
  selector:
    matchLabels:
      ec2_metadata_for: {pod_role}
  template:
    metadata:
      labels:
        name: {pod_role}-mock-metadata
        is_ec2_metadata: "True"
        ec2_metadata_for: {pod_role}
    spec:
      containers:
        - image: satvidh/ectou-metadata
          name: ectou-metadata
          imagePullPolicy: IfNotPresent
"""
        body = yaml.load(deployment_yaml, Loader=yaml.SafeLoader)
        return body
