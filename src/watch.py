from kubernetes import client, config, watch
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: This needs a satvidh/ectou_metadata image.
# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()

v1 = client.CoreV1Api()
extensions_v1_beta1 = client.ExtensionsV1beta1Api()
w = watch.Watch()

namespace = 'default'

deployment_template = \
"""
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {name}-mock-metadata
  labels:
    ec2_metadata_for: {name}
spec:
  selector:
    matchLabels:
      ec2_metadata_for: {name}
  template:
    metadata:
      labels:
        name: {name}-mock-metadata
        is_ec2_metadata: "True"
        ec2_metadata_for: {name}
    spec:
      containers:
        - image: satvidh/ectou-metadata
          name: ectou-metadata
          imagePullPolicy: IfNotPresent
"""
metadata_deployments = {}
cont = None
logger.info("Find mock metadata deployments.")
deployments_response = extensions_v1_beta1.list_deployment_for_all_namespaces(
    label_selector="is_ec2_metadata=True")
while True:
    deployments = deployments_response.items
    for deployment in deployments:
        ec2_metadata_for = deployment.metadata.labels["ec2_metadata_for"]
        logger.info(f"Found deployment {ec2_metadata_for}.")
        metadata_deployments[ec2_metadata_for] = deployment
    cont = deployments_response.metadata._continue
    if cont is None:
        break
    deployments_response = extensions_v1_beta1.list_deployment_for_all_namespaces(
        _continue=cont,
        label_selector="is_ec2_metadata=True")
logger.info("Done with mock metadata deployments.")

for event in w.stream(v1.list_pod_for_all_namespaces, _request_timeout=0):
    logger.info("Event: %s %s" % (event['type'], event['object'].metadata.name))
    if event['type'] == 'ADDED':
        obj = event['object']
        if obj.api_version == 'v1':
            logger.info("Check if pod is a candidate for mock metadata.")
            annotations = obj.metadata.annotations
            # If the object has a pod role, then create a mock metadata instance
            # if there is not one for that pod role.
            if annotations:
                pod_role = annotations.get('iam.amazonaws.com/role', None)
                if pod_role:
                    logger.info(f"Found a pod with pod role={pod_role}.")
                    if pod_role not in metadata_deployments:
                        logger.info(f"Did not find mock metadata for {pod_role}.")
                        deployment_yaml = deployment_template.format(name=pod_role)
                        body = yaml.load(deployment_yaml)
                        extensions_v1_beta1.create_namespaced_deployment(
                            namespace=namespace,
                            body=body)
                        logger.info(f"Deployed mock metadata named {pod_role}")
                        continue
            logger.info(f"Pod is not a candidate for mock metadata"
                         " because it does not have a pod role annotation.")
            # If the pod is an mock metadata pod, then find its deployment
            # and add it to the metadata_deployments dictionary.
            logger.info("Check if pod is a mock metadata pod.")
            labels = obj.metadata.labels
            is_mock_metadata_pod = False
            if labels:
                is_ec2_metadata = labels.get("is_ec2_metadata", None)
                if is_ec2_metadata == "True":
                    ec2_metadata_for = labels["ec2_metadata_for"]
                    deployments_response = extensions_v1_beta1.list_deployment_for_all_namespaces(
                        label_selector="ec2_metadata_for={}".format(ec2_metadata_for))
                    if deployments_response:
                        is_mock_metadata_pod = True
                        logger.info(f"Pod provides metadata for role {ec2_metadata_for}.")
                        metadata_deployments[ec2_metadata_for] = deployments_response
            if not is_mock_metadata_pod:
                logger.info(f"Pod is not a mock metadata pod.")
            # metadata = obj['metadata']
            # annotations = metadata.get('annotations', None)
            # if annotations:
            #     pod_role = annotations.get('iam.amazonaws.com/role', None)
            #     if pod_role:
            #         body = client.V1Pod()
            #         print(body)
