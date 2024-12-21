import pytest
import os
import json

@pytest.fixture(autouse=True)
def clean_test_files():
    """Cleanup any test files after each test"""
    yield
    # Cleanup after test
    test_files = ['test_cookbooks.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)