import pytest
import event_handlers

class TestAddedEventHandler(object):
    @pytest.fixture()
    def pod(self):
        yield object()

    @pytest.fixture()
    def mock_pods(self, mocker):
        pods = mocker.patch("pods.Pods", autospec=True).return_value
        yield pods

    @pytest.fixture()
    def handler(self, mock_pods):
        """
        :param mock_pods:   The handlers instantiate an instance of pods.Pods in
                            their __init__(). Ensure the mock exists.
        """
        h = event_handlers.create_event_handler(event="ADDED")
        yield h

    def test_handle_given_pod_does_not_have_a_pod_role(self,
                                                       handler,
                                                       pod,
                                                       mock_pods):
        # GIVEN
        # pod
        mock_pods.get_pod_role.return_value = None

        # WHEN
        handler.handle(pod)

        # THEN
        mock_pods.get_pod_role.assert_called_with(pod)
        mock_pods.ensure_ec2_metadata.assert_not_called()

    def test_handle_given_pod_has_a_pod_role(self,
                                             handler,
                                             pod,
                                             pod_role,
                                             mock_pods):
        # GIVEN
        # pod
        mock_pods.get_pod_role.return_value = pod_role

        # WHEN
        handler.handle(pod)

        # THEN
        mock_pods.get_pod_role.assert_called_with(pod)
        mock_pods.ensure_ec2_metadata.assert_called_with(pod)
