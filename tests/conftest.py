import os
import tempfile

import pytest



@pytest.fixture(scope='session')
def splinter_webdriver(request):
    return request.config.option.splinter_webdriver or 'chrome'


@pytest.fixture(scope='session')
def splinter_webdriver_executable(request, splinter_webdriver):
    """Webdriver executable directory."""
    executable = request.config.option.splinter_webdriver_executable
    if not executable and splinter_webdriver == 'chrome':
        from chromedriver_binary import chromedriver_filename
        executable = chromedriver_filename
    return os.path.abspath(executable) if executable else None


def pytest_addoption(parser):
    parser.addoption(
        '--skip-webtest',
        action='store_true',
        dest="skip_webtest",
        default=False,
        help="skip marked webtest tests")


def pytest_configure(config):
    mark_expr = []

    if config.option.markexpr:
        mark_expr.append(config.option.markexpr)

    if config.option.skip_webtest:
        mark_expr.append('not webtest')
    if mark_expr:
        setattr(config.option, 'markexpr', ' and '.join(mark_expr))
