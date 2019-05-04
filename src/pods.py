class Pods(object):
    __POD_ROLE_ANNOTATION_KEY = "iam.amazonaws.com/role"
    def get_pod_role(self, pod):
        """
        If pod annotation has a __POD_ROLE_ANNOTATION_KEY, then return it.
        Return None otherwise.

        :param pod:     A V1Pod() instance.
        :return pod role if the pod role annotation exists, None otherwise.
        """
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
        """
        Ensure that the ec2_metatadata instance exists.

        :param  pod:    The pod that needs the ec2_metadata.
        :return None
        """
        from deployments import Deployments

        pod_role = self.get_pod_role(pod)
        deployments = Deployments()
        deployments.ensure_ec2_metadata_deployment(pod_role)


