import pytest
from kubernetes import client

class TestPods(object):
    @pytest.fixture()
    def pod_ip(self):
        yield "10.1.2.10"

    @pytest.fixture()
    def container_id(self):
        yield "ContainerIDWhichIsSomeVeryLongHexadecimalString"

    @pytest.fixture()
    def v1pod_with_pod_role(self, v1pod, pod_role):
        instance = v1pod
        instance.metadata = client.V1ObjectMeta()
        instance.metadata.annotations = {
            "iam.amazonaws.com/role": pod_role
        }
        yield instance

    @pytest.fixture()
    def v1pod_with_pod_role_and_status(
        self, 
        v1pod_with_pod_role, 
        pod_role, 
        pod_ip,
        container_id):
        instance = v1pod_with_pod_role
        # Status object for container_id and pod_ip
        instance.status = client.V1PodStatus()
        # pod_id
        instance.status.pod_ip = pod_ip
        # Container status for container_id
        image = "image"        
        image_id = "ImageIDWhichIsSomeVeryLongHexadecimalString"
        name = "name"

        container_status = client.V1ContainerStatus(
            container_id=container_id, 
            image=image, 
            image_id=image_id, 
            name=name, 
            ready=True, 
            restart_count=1)
        instance.container_statuses = [container_status]

        yield instance

    @pytest.fixture()
    def pods(self):
        import pods
        instance = pods.Pods()
        yield instance

    @pytest.fixture()
    def mock_deployments(self, mocker):
        deployments = mocker.patch("deployments.Deployments", autospec=True).return_value
        yield deployments

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
        self, v1pod_with_pod_role_and_status, pod_role, pods, pod_ip, container_id, 
        mock_deployments, mock_containerama
    ):
        # GIVEN
        # v1pod_with_pod_role
        # pod_role
        # pods
        # mock_deployments

        # WHEN
        pods.ensure_ec2_metadata(v1pod_with_pod_role_and_status)

        # THEN
        mock_deployments.ensure_ec2_metadata_deployment.assert_called_with(pod_role)
        mock_containerama.join_cast(container_id, pod_role)
