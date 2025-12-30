import os
import tempfile
import pytest
from agentic_layer.validators import Validator, ValidationError


class TestValidator:
    """Tests for the Validator class"""

    def test_validate_spec_missing(self):
        """Test spec validation with missing file"""
        is_valid, error = Validator.validate_spec("/nonexistent/spec.md")
        assert is_valid is False
        assert "not found" in error

    def test_validate_spec_empty(self):
        """Test spec validation with empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            spec_path = f.name

        try:
            is_valid, error = Validator.validate_spec(spec_path)
            assert is_valid is False
            assert "empty" in error.lower()
        finally:
            os.unlink(spec_path)

    def test_validate_spec_valid(self):
        """Test spec validation with valid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# Goal
This is the goal

## User Stories
- As a user, I want...

## Acceptance Criteria
- Feature works correctly
            """)
            spec_path = f.name

        try:
            is_valid, error = Validator.validate_spec(spec_path)
            assert is_valid is True
            assert error is None
        finally:
            os.unlink(spec_path)

    def test_validate_plan_valid(self):
        """Test plan validation with valid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# Architecture Overview
System design...

## File Changes
- file1.py
- file2.py

## Testing Strategy
Test approach...
            """)
            plan_path = f.name

        try:
            is_valid, error = Validator.validate_plan(plan_path)
            assert is_valid is True
            assert error is None
        finally:
            os.unlink(plan_path)

    def test_validate_tasks_valid(self):
        """Test tasks validation with valid file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
---yaml
tasks:
  - id: 1
    description: "Test task"
    status: pending
    action: create_file
    path: "test.py"
    context_files: []
---

# Tasks
- [ ] Test task
            """)
            tasks_path = f.name

        try:
            is_valid, error, data = Validator.validate_tasks(tasks_path)
            assert is_valid is True
            assert error is None
            assert data is not None
            assert len(data["tasks"]) == 1
        finally:
            os.unlink(tasks_path)

    def test_validate_tasks_invalid_status(self):
        """Test tasks validation with invalid status"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
---yaml
tasks:
  - id: 1
    description: "Test task"
    status: invalid_status
    action: create_file
    path: "test.py"
---
            """)
            tasks_path = f.name

        try:
            is_valid, error, data = Validator.validate_tasks(tasks_path)
            assert is_valid is False
            assert "invalid status" in error.lower()
        finally:
            os.unlink(tasks_path)

    def test_validate_file_content(self):
        """Test file content validation"""
        # Valid content
        is_valid, error = Validator.validate_file_content("def test():\n    pass\n", "py")
        assert is_valid is True

        # Empty content
        is_valid, error = Validator.validate_file_content("", "py")
        assert is_valid is False

        # Content with unwanted patterns
        is_valid, error = Validator.validate_file_content("I apologize, but...", "py")
        assert is_valid is False
