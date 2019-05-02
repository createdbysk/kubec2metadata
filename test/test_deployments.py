import pytest
import collections
import deployments
import itertools
import yaml

class TestDeployments(object):
    @pytest.fixture()
    def label_selector_key(self):
        return "key"

    @pytest.fixture()
    def label_selector_value(self):
        return "value"

    @pytest.fixture()
    def mock_extensions_v1_beta_api(self, mocker):
        extensions_v1_beta_api = mocker.patch(
            "kubernetes.client.ExtensionsV1beta1Api",
            autospec=True).return_value
        yield extensions_v1_beta_api

    @pytest.fixture()
    def deployments(self, mock_extensions_v1_beta_api):
        """
        :param mock_extensions_v1_beta_api: The object is created in the Deployments()
                                            constructor.
        """
        instance = deployments.Deployments()
        yield instance

    @pytest.mark.parametrize(
        "lists_of_items, _continues",
        [
            ([["1", "2", "3"]], []),
            ([["1", "2", "3"], ["4", "5", "6"]], ["dork"])
        ]
    )
    def test_deployments_for_selector(self,
                                      lists_of_items,
                                      _continues,
                                      label_selector_key,
                                      label_selector_value,
                                      deployments,
                                      mock_extensions_v1_beta_api,
                                      mocker):
        # GIVEN
        # function parameters

        # itertools.chain() chains the contents of the lists.
        # from_iterable takes an argument that is a list of iterables.
        expected_result = list(itertools.chain.from_iterable(lists_of_items))
        # The last _continue must always be None.
        _continues.append(None)
        MockDeployments = collections.namedtuple("MockDeployments",
                                                  field_names=["items", "metadata"])
        # Cannot use a namedtuple here because namedtuple does not
        # allow field_names that start with _. So _continue cannot
        # be a field_name.
        class MockMetadata(object):
            def __init__(self, _continue):
                self._continue = _continue

        values =  [
                    MockDeployments(items=items,
                                    metadata=MockMetadata(_continue=_continue))
                    for items, _continue in zip(lists_of_items, _continues)
        ]

        mock_extensions_v1_beta_api.list_deployment_for_all_namespaces.side_effect = values

        # WHEN
        actual_result = [
            deployment for deployment in deployments.get_selected_deployments(
                label_selector_key,
                label_selector_value
            )
        ]

        # THEN
        assert actual_result == expected_result

        # The first call does not pass the _continue.
        # Subsequent calls do pass _continue.
        # The functions should never call _continue=None.
        calls = [
            mocker.call(
                label_selector=f"{label_selector_key}={label_selector_value}"
            )
        ] + [
            mocker.call(
                _continue=_continue,
                label_selector=f"{label_selector_key}={label_selector_value}"
            )
            for _continue in _continues[:-1]
        ]
        mock_extensions_v1_beta_api.list_deployment_for_all_namespaces.assert_has_calls(
            calls
        )

    @pytest.fixture()
    def body(self, pod_role):
        deployment_spec = f"""
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {pod_role}-mock-metadata
  labels:
    ec2_metadata_for: {pod_role}
spec:
  selector:
    matchLabels:
      ec2_metadata_for: {pod_role}
  template:
    metadata:
      labels:
        name: {pod_role}-mock-metadata
        is_ec2_metadata: "True"
        ec2_metadata_for: {pod_role}
    spec:
      containers:
        - image: satvidh/ectou-metadata
          name: ectou-metadata
          imagePullPolicy: IfNotPresent
"""
        expected_body = yaml.load(deployment_spec, Loader=yaml.SafeLoader)
        yield expected_body

    @pytest.mark.parametrize(
        "prior_deployments",
        [
            [],
            [object()]
        ]
    )
    def test_ensure_ec2_metadata_deployment(self,
                                        prior_deployments,
                                        body,
                                        namespace,
                                        pod_role,
                                        deployments,
                                        mock_extensions_v1_beta_api,
                                        mocker):
        # GIVEN
        # body
        # namespace
        # pod_role
        # prior_deployments
        mock_get_selected_deployments = mocker.patch.object(
            deployments,
            "get_selected_deployments"
        )
        mock_get_selected_deployments.return_value = prior_deployments

        mock_extensions_v1_beta_api.create_namespaced_deployment.return_value = None

        # WHEN
        deployments.ensure_ec2_metadata_deployment(pod_role)

        # THEN
        mock_get_selected_deployments.assert_called_with("ec2_metadata_for",
                                                         pod_role)
        # If there were no prior_deployments, then expect
        # ensure_ec2_metadata_deployment creates a deployment.
        if len(prior_deployments) == 0:
            mock_extensions_v1_beta_api.create_namespaced_deployment.assert_called_with(
                namespace=namespace,
                body=body
            )
        else:
            mock_extensions_v1_beta_api.create_namespaced_deployment.assert_not_called()
