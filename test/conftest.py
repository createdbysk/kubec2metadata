import pytest

@pytest.fixture()
def namespace():
    return "default"

@pytest.fixture()
def pod_role():
    return "pod-role"
