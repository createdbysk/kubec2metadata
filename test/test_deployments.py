import pytest
import collections
import deployments
import itertools

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
            ([["1", "2", "3"]], [None]),
            ([["1", "2", "3"], ["4", "5", "6"]], ["dork", None])
        ]
    )
    def test_deployments_for_selector(self,
                                      lists_of_items,
                                      _continues,
                                      label_selector_key,
                                      label_selector_value,
                                      deployments,
                                      mock_extensions_v1_beta_api):
        # GIVEN
        # function parameters

        # itertools.chain() chains the contents of the lists.
        # from_iterable takes an argument that is a list of iterables.
        expected_result = list(itertools.chain.from_iterable(lists_of_items))

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
