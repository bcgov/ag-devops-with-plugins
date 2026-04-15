"""
Pytest configuration for ag-devops test harness.
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--update-fixtures",
        action="store_true",
        default=False,
        help="Regenerate golden fixture files in tests/fixtures/expected/",
    )


@pytest.fixture
def update_fixtures(request):
    return request.config.getoption("--update-fixtures")

