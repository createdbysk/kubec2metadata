from kubernetes import client, config, watch
import yaml
import logging
import typing
import deployments
#import docker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# TODO: This needs a satvidh/ectou_metadata image.
# Configs can be set in Configuration class directly or using helper utility
try:
    logger.info("Load config...")
    config.load_incluster_config()
    logger.info("Loaded in-cluster config.")
except config.config_exception.ConfigException:
    config.load_kube_config()
    logger.info("Loaded kube config.")

#docker_client = docker.from_env
v1 = client.CoreV1Api()
w = watch.Watch()
extensions_v1_beta1 = client.ExtensionsV1beta1Api()
deployments_instance = deployments.Deployments()

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
pods_with_role = {}
logger.info("Find mock metadata deployments.")
for deployment in deployments_instance.get_selected_deployments("is_ec2_metadata", "True"):
    ec2_metadata_for = deployment.metadata.labels["ec2_metadata_for"]
    logger.info(f"Found deployment {ec2_metadata_for}.")
    metadata_deployments[ec2_metadata_for] = deployment

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
                        logger.info(f"Did not find mock metadata pod for {pod_role}.")
                        deployment_yaml = deployment_template.format(name=pod_role)
                        body = yaml.load(deployment_yaml)
                        extensions_v1_beta1.create_namespaced_deployment(
                            namespace=namespace,
                            body=body)
                        logger.info(f"Deployed mock metadata named {pod_role}")
                        continue
                    else:
                        logger.info(f"Found mock metadata pod for {pod_role}")
                        continue

            logger.info(f"Pod is not a candidate for mock metadata"
                         " because it does not have a pod role annotation.")
            # If the pod is an mock metadata pod, then find its deployment
            # and add it to the metadata_deployments dictionary.
            logger.info("Check if pod is a mock metadata pod.")
            labels = obj.metadata.labels
            is_ec2_metadata_pod = False
            if labels:
                is_ec2_metadata = labels.get("is_ec2_metadata", None)
                if is_ec2_metadata == "True":
                    ec2_metadata_for = labels["ec2_metadata_for"]
                    for deployment in deployments_instance.get_selected_deployments(
                        "ec2_metadata_for", ec2_metadata_for):
                        is_ec2_metadata_pod = True
                        logger.info(f"Pod provides metadata for role {ec2_metadata_for}.")
                        metadata_deployments[ec2_metadata_for] = deployment
            if not is_ec2_metadata_pod:
                logger.info(f"Pod is not a mock metadata pod.")
            # metadata = obj['metadata']
            # annotations = metadata.get('annotations', None)
            # if annotations:
            #     pod_role = annotations.get('iam.amazonaws.com/role', None)
            #     if pod_role:
            #         body = client.V1Pod()
            #         print(body)
