import pytest

class TestGmail:
    @pytest.fixture
    def foo(self):
        return "foo"

    def test_foo(self, foo):
        assert not foo == "bar"
