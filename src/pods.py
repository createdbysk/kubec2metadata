class Pods(object):
    __POD_ROLE_ANNOTATION_KEY = "iam.amazonaws.com/role"
    def get_pod_role(self, pod):
        # If the pod has an annotation with key Pods.__POD_ROLE_ANNOTATION_KEY
        # that is the pod_role.
        if pod is not None:
            if pod.metadata is not None:
                if pod.metadata.annotations is not None:
                    if Pods.__POD_ROLE_ANNOTATION_KEY \
                        in pod.metadata.annotations:
                        return pod.metadata.annotations[
                            Pods.__POD_ROLE_ANNOTATION_KEY
                    ]
        # Otherwise, return None.
        return None

    def ensure_ec2_metadata(self, pod):
        raise NotImplementedError
