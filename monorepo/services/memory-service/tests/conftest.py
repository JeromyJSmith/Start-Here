"""
Pytest configuration for Memory Service testing.
Following T-1 to T-5 coding guide principles.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import sys

# Add memory-service to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def temp_directory():
    """Create temporary directory for test isolation."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="function") 
def mock_memory_store():
    """Mock memory store for unit tests."""
    store = Mock()
    store.save = AsyncMock(return_value={"id": "test_id", "status": "saved"})
    store.retrieve = AsyncMock(return_value={"data": "test_data"})
    store.delete = AsyncMock(return_value=True)
    store.search = AsyncMock(return_value=[{"id": "1", "content": "test"}])
    return store

@pytest.fixture(scope="function")
def mock_cognee_client():
    """Mock Cognee client for integration tests."""
    client = Mock()
    client.add = AsyncMock(return_value={"status": "processed"})
    client.search = AsyncMock(return_value={"results": []})
    client.prune = AsyncMock(return_value={"deleted": 0})
    return client

@pytest.fixture(scope="function")
def mock_memento_client():
    """Mock Memento MCP client for integration tests."""
    client = Mock()
    client.store_memory = AsyncMock(return_value={"id": "mem_123"})
    client.retrieve_memory = AsyncMock(return_value={"content": "memory"})
    client.search_memories = AsyncMock(return_value=[])
    return client

@pytest.fixture(scope="function")
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "id": "test_memory_123",
        "content": "This is a test memory",
        "metadata": {
            "timestamp": "2025-01-31T12:00:00Z",
            "source": "test",
            "tags": ["test", "memory"]
        },
        "embeddings": [0.1, 0.2, 0.3, 0.4, 0.5]
    }

@pytest.fixture(scope="function")
def sample_query():
    """Sample query data for testing."""
    return {
        "text": "find memories about testing",
        "filters": {"tags": ["test"]},
        "limit": 10,
        "threshold": 0.7
    }

@pytest.fixture(scope="function")
def mock_database():
    """Mock database connection for integration tests."""
    with patch('memory_service.database.connect') as mock_connect:
        mock_conn = Mock()
        mock_conn.execute = AsyncMock(return_value=[])
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.close = AsyncMock()
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture(scope="function")
def mock_vector_db():
    """Mock vector database for integration tests."""
    with patch('memory_service.vector_store.VectorStore') as mock_vs:
        instance = Mock()
        instance.add_vectors = AsyncMock(return_value=True)
        instance.search_vectors = AsyncMock(return_value=[])
        instance.delete_vectors = AsyncMock(return_value=True)
        mock_vs.return_value = instance
        yield instance

# Test markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Pure logic unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (database, memory stores)"  
    )
    config.addinivalue_line(
        "markers", "async_test: Tests that require async execution"
    )
    config.addinivalue_line(
        "markers", "memory_store: Tests involving memory storage operations"
    )

def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on patterns."""
    for item in items:
        # Mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
            item.add_marker(pytest.mark.async_test)
        
        # Mark integration tests  
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid or "spec.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Mark memory store tests
        if any(keyword in item.nodeid.lower() for keyword in ["memory", "cognee", "memento"]):
            item.add_marker(pytest.mark.memory_store)