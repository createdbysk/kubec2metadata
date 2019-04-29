#!/usr/bin/env python
import os
import yaml
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXPECTED_API_VERSION = "v1"
KUBERNETES_CLUSTER_NAME = "docker-for-desktop-cluster"
KUBERNETES_CLUSTER_USER_NAME = "docker-for-desktop"
SANDBOX_CONTEXT_NAME = "k8s.sandbox.ksops.net"

config_file_path = os.environ['CONFIG_FILE_PATH']
new_config = {}
with open(config_file_path, "r") as fp:
    try:
        config = yaml.load(fp, Loader=yaml.SafeLoader)
        new_config = config.copy()
        new_config["apiVersion"] = config["apiVersion"]
        if new_config["apiVersion"] != EXPECTED_API_VERSION:
            raise RuntimeError("Expected config apiVersion {expected}. Found apiVersion {actual}".format(
                expected=EXPECTED_API_VERSION,
                actual=new_config["apiVersion"]
            ))
        new_config["clusters"] = [
            cluster for cluster in config["clusters"]
            if cluster["name"] == KUBERNETES_CLUSTER_NAME
        ]
        if not new_config["clusters"]:
            raise RuntimeError("Did not find a cluster named {}".format(
                KUBERNETES_CLUSTER_NAME
            ))
        new_config["users"] = [
            user for user in config["users"]
            if user["name"] == KUBERNETES_CLUSTER_USER_NAME
        ]
        if not new_config["users"]:
            raise RuntimeError("Did not find a user named {}".format(
                KUBERNETES_CLUSTER_USER_NAME
            ))
        new_config["contexts"] = [
            {
                'name': SANDBOX_CONTEXT_NAME,
                'context': {
                    'cluster': KUBERNETES_CLUSTER_NAME,
                    'user': KUBERNETES_CLUSTER_USER_NAME
                }
            }
        ]
        # This container expects that the user has setup dockerhost
        # (https://github.com/qoomon/docker-host)
        # for this container to access the Kubernetes on the host machine.
        new_config["clusters"][0]["cluster"]["server"] = \
            new_config["clusters"][0]["cluster"]["server"].replace(
                "localhost", "dockerhost"
            )
        new_config["current-context"] = SANDBOX_CONTEXT_NAME
        print(yaml.dump(new_config))
    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)
