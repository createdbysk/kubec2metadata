import pytest
from kubernetes import client

class TestPods(object):
    @pytest.fixture()
    def v1pod(self):
        instance = client.V1Pod()
        yield instance

    @pytest.fixture()
    def pods(self):
        import pods
        instance = pods.Pods()
        yield instance

    def test_get_pod_role_given_pod_does_not_have_any_metadata(self,
                                                               v1pod,
                                                               pods):
        # GIVEN
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_not_have_any_annotations(self,
                                                                  v1pod,
                                                                  pods):
        # GIVEN
        v1pod.metadata = client.V1ObjectMeta()
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_not_have_pod_role_annotation(self,
                                                                      v1pod,
                                                                      pods):
        # GIVEN
        v1pod.metadata = client.V1ObjectMeta()
        v1pod.metadata.annotations = {
            "not_pod_role": "not_it"
        }
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_has_pod_role_annotation(self,
                                                                 v1pod,
                                                                 pod_role,
                                                                 pods):
        # GIVEN
        v1pod.metadata = client.V1ObjectMeta()
        v1pod.metadata.annotations = {
            "iam.amazonaws.com/role": pod_role
        }
        expected_result = pod_role

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result
