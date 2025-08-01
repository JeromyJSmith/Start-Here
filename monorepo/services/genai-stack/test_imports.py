#!/usr/bin/env python3
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Python path:", sys.path)

try:
    import langchain_neo4j
    print("✓ langchain_neo4j imported successfully")
except ImportError as e:
    print("✗ Failed to import langchain_neo4j:", e)

try:
    import neo4j
    print("✓ neo4j imported successfully")
except ImportError as e:
    print("✗ Failed to import neo4j:", e)

try:
    import streamlit
    print("✓ streamlit imported successfully")
except ImportError as e:
    print("✗ Failed to import streamlit:", e)