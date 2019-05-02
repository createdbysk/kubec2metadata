class Pods(object):
    def get_pod_role(self, pod):
        raise NotImplementedError()

    def ensure_ec2_metadata(self, pod):
        raise NotImplementedError
