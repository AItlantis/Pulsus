# conftest.py - Pytest configuration for Pulsus tests
# Disables pytest-qt plugin which is not needed for these tests

import sys

# Block pytest-qt from loading by disabling it explicitly
def pytest_configure(config):
    """Disable pytest-qt plugin."""
    config.pluginmanager.set_blocked('pytest_qt')
