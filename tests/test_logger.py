import os
import tempfile
import pytest
from agentic_layer.logger import AgentLogger


class TestLogger:
    """Tests for the AgentLogger class"""

    def test_logger_init(self):
        """Test logger initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(tmpdir, enabled=True, level="INFO")
            assert logger.enabled is True
            assert os.path.exists(logger.history_dir)

    def test_logger_disabled(self):
        """Test disabled logger"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(tmpdir, enabled=False)
            assert logger.enabled is False
            # Logging should not raise errors when disabled
            logger.info("Test message")
            logger.error("Test error")

    def test_log_operation(self):
        """Test logging operations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(tmpdir, enabled=True)

            # Log an operation
            logger.log_operation("test_operation", {"key": "value"})

            # Check history
            history = logger.get_history("test_operation", limit=1)
            assert len(history) == 1
            assert history[0]["operation"] == "test_operation"
            assert history[0]["data"]["key"] == "value"

    def test_log_task_execution(self):
        """Test logging task execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(tmpdir, enabled=True)

            task = {
                "id": 1,
                "description": "Test task",
                "action": "create_file",
                "path": "test.py"
            }

            # Log successful execution
            logger.log_task_execution(task, success=True)

            # Check history
            history = logger.get_task_history(limit=1)
            assert len(history) == 1
            assert history[0]["data"]["success"] is True

    def test_clear_history(self):
        """Test clearing history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(tmpdir, enabled=True)

            # Create some history
            logger.log_operation("op1", {"data": 1})
            logger.log_operation("op2", {"data": 2})

            # Verify history exists
            assert len(logger.get_history()) >= 2

            # Clear history
            logger.clear_history()

            # Verify history is empty
            assert len(logger.get_history()) == 0
