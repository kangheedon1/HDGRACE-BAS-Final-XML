"""
테스트 설정
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

# 테스트용 임시 디렉토리
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

# 비동기 테스트를 위한 이벤트 루프
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 테스트용 설정
@pytest.fixture
def test_config():
    return {
        "app": {
            "name": "HDGRACE Test",
            "version": "1.0.0",
            "environment": "test",
            "debug": True
        },
        "database": {
            "type": "sqlite",
            "name": ":memory:",
            "echo": False
        },
        "xml_generator": {
            "target_features": 100,  # 테스트용 작은 숫자
            "target_size_mb": 1,
            "bas_version": "29.3.1",
            "max_generation_time": 60,
            "output_path": "./test_output",
            "validation_enabled": True,
            "correction_enabled": True
        },
        "logging": {
            "level": "DEBUG",
            "file_path": "./test_logs/test.log"
        }
    }