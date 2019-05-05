import pytest
from kubernetes import client

class TestPods(object):
    @pytest.fixture()
    def v1pod(self):
        instance = client.V1Pod()
        yield instance

    @pytest.fixture()
    def v1pod_with_pod_role(self, v1pod, pod_role):
        v1pod.metadata = client.V1ObjectMeta()
        v1pod.metadata.annotations = {
            "iam.amazonaws.com/role": pod_role
        }
        yield v1pod

    @pytest.fixture()
    def v1pod_with_pod_role_and_status(self, v1pod_with_pod_role):
        v1pod_with_pod_role.status = client.V1PodStatus()
        v1pod_with_pod_role.status.container_status

    @pytest.fixture()
    def pods(self):
        import pods
        instance = pods.Pods()
        yield instance

    @pytest.fixture()
    def mock_containerama(self, mocker):
        containerama = mocker.patch("containerama.Containerama", autospec=True).return_value
        yield containerama

    def test_get_pod_role_given_pod_does_not_have_any_metadata(
        self, v1pod, pods
    ):
        # GIVEN
        # v1pod
        # pods
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_not_have_any_annotations(
        self, v1pod, pods
    ):
        # GIVEN
        # v1pod
        # pods
        v1pod.metadata = client.V1ObjectMeta()
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_not_have_pod_role_annotation(
        self, v1pod, pods
    ):
        # GIVEN
        # v1pod
        # pods
        v1pod.metadata = client.V1ObjectMeta()
        v1pod.metadata.annotations = {
            "not_pod_role": "not_it"
        }
        expected_result = None

        # WHEN
        actual_result = pods.get_pod_role(v1pod)

        # THEN
        assert expected_result == actual_result

    def test_get_pod_role_given_pod_does_has_pod_role_annotation(
        self, v1pod_with_pod_role, pod_role, pods
    ):
        # GIVEN
        # v1pod_with_pod_role
        # pod_role
        # pods
        expected_result = pod_role

        # WHEN
        actual_result = pods.get_pod_role(v1pod_with_pod_role)

        # THEN
        assert expected_result == actual_result

    def test_ensure_ec2_metadata(
        self, v1pod_with_pod_role, pod_role, pods, mock_containerama
    ):
        # GIVEN
        # v1pod_with_pod_role
        # pod_role
        # pods
        # mock_containerama

        # WHEN
        pods.ensure_ec2_metadata(v1pod_with_pod_role)

        # THEN
        mock_containerama.join_cast.assert_called_with(pod_role)