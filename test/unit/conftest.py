import os
import pytest
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "test.test_django_project.test_django_project.settings"
)


@pytest.fixture(scope="session", autouse=True)
def setup_django():
    pass


def pytest_configure():
    # can modify settings here..
    django.setup()
