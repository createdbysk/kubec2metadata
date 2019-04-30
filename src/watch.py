from kubernetes import client, config, watch
import yaml

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

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
  name: {name}
  labels:
    name: {name}
    ec2_metadata_for: {name}
spec:
  template:
    metadata:
      labels:
        name: {name}
        is_ec2_metadata: True
        ec2_metadata_for: {name}
    spec:
      containers:
        - image: satvidh/ectou_metadata
          name: ectou_metadata
          imagePullPolicy: IfNotPresent
"""
metadata_deployments = {}
cont = None
while True:
    deployments_response = v1.list_deployments_for_all_namespaces(_continue=cont,
                                                                  label_selector="is_ec2_metadata=True")
    cont = deployments_response.metadata._continue
    deployments = deployments_response.items
    for deployment in deployments:
        ec2_metadata_for = deployment["ec2_metadata_for"]
        metadata_deployments[ec2_metadata_for] = deployment
    if not cont:
        break

print(metadata_deployments)
for event in w.stream(v1.list_pod_for_all_namespaces, _request_timeout=0):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    if event['type'] == 'ADDED':
        obj = event['object']
        if obj.api_version == 'v1':
            annotations = obj.metadata.annotations
            if annotations:
                pod_role = annotations.get('iam.amazonaws.com/role', None)
                if pod_role:
                    print("YOOOO HOOO!!! found you")
                    if not metadata_deployments.has_key(pod_role):
                        deployment_yaml = deployment_template.format(name=pod_role)
                        body = yaml.load(deployment_yaml)
                        extensions_v1_beta1.create_namespaced_deployment(
                            namespace=namespace,
                            body=body)
                        continue
            labels = obj.metadata.labels
            if labels:
                is_ec2_metadata = labels.get("is_ec2_metadata", None)
                if is_ec2_metadata == "True":
                    ec2_metadata_for = labels["ec2_metadata_for"]
                    deployments_response = v1.list_deployments_for_all_namespaces(
                        _continue=cont,
                        label_selector="ec2_metadata_for={}".format(ec2_metadata_for))
                    if deployments_response:
                        metadata_deployments[ec2_metadata_for] = deployments_response

            # metadata = obj['metadata']
            # annotations = metadata.get('annotations', None)
            # if annotations:
            #     pod_role = annotations.get('iam.amazonaws.com/role', None)
            #     if pod_role:
            #         body = client.V1Pod()
            #         print(body)
