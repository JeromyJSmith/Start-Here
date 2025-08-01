"""
Pytest configuration and fixtures for SuperClaude Framework testing.
Following T-1 (MUST) principle: Colocate unit tests, separate from integration tests.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add SuperClaude to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "SuperClaude"))

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "test_mode": True,
        "log_level": "DEBUG",
        "temp_dir": None
    }

@pytest.fixture(scope="function")
def temp_directory():
    """Create a temporary directory for test isolation."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function")
def mock_file_system():
    """Mock file system operations for unit tests."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open') as mock_open:
        mock_exists.return_value = True
        yield {
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'open': mock_open
        }

@pytest.fixture(scope="function")
def mock_subprocess():
    """Mock subprocess operations for unit tests."""
    with patch('subprocess.run') as mock_run, \
         patch('subprocess.Popen') as mock_popen:
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        yield {
            'run': mock_run,
            'popen': mock_popen
        }

@pytest.fixture(scope="function")
def mock_network():
    """Mock network operations for unit tests."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }

@pytest.fixture(scope="function")
def sample_config():
    """Sample configuration data for testing."""
    return {
        "features": {
            "cli_integration": True,
            "web_ui": True,
            "api_server": False
        },
        "profiles": {
            "default": "developer",
            "available": ["minimal", "developer", "quick"]
        },
        "version": "1.0.0"
    }

@pytest.fixture(scope="function")
def sample_profile():
    """Sample profile data for testing."""
    return {
        "name": "test_profile",
        "description": "Test profile for unit tests",
        "components": ["core", "cli"],
        "settings": {
            "debug": True,
            "verbose": False
        }
    }

# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (pure logic, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (database, filesystem, network)"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test (full system workflow)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on location."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark unit tests (default for tests not in integration folders)
        elif "unit" in item.nodeid or "integration" not in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)