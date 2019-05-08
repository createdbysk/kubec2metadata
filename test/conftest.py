import pytest

@pytest.fixture()
def namespace():
    return "default"

@pytest.fixture()
def pod_role():
    return "pod-role"

@pytest.fixture()
def v1pod():
    from kubernetes import client
    instance = client.V1Pod()
    yield instance
