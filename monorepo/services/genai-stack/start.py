#!/usr/bin/env python3
import os
import sys
import time

print("GenAI Stack starting...")
print(f"Python: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Test imports
print("\nTesting imports...")
try:
    import streamlit
    print("✓ Streamlit imported")
except:
    print("✗ Streamlit import failed")

try:
    import neo4j
    print("✓ Neo4j imported")
except:
    print("✗ Neo4j import failed")

try:
    import langchain_neo4j
    print("✓ LangChain Neo4j imported")
except:
    print("✗ LangChain Neo4j import failed")

# Keep container running for debugging
print("\nContainer is running. Check imports above.")
while True:
    time.sleep(60)
    print(".", end="", flush=True)