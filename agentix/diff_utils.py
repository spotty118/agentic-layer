"""Diff utilities for viewing and managing file changes."""
import os
import difflib
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime


class DiffViewer:
    """Handle diff generation and viewing for file changes."""

    def __init__(self, agent_dir: str):
        self.agent_dir = agent_dir
        self.backup_dir = os.path.join(agent_dir, "backups")

    def generate_unified_diff(self, original: str, modified: str,
                            filepath: str, context_lines: int = 3) -> str:
        """
        Generate a unified diff between original and modified content.

        Args:
            original: Original file content
            modified: Modified file content
            filepath: Path to the file (for display)
            context_lines: Number of context lines around changes

        Returns:
            Unified diff string
        """
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
            lineterm='',
            n=context_lines
        )

        return ''.join(diff)

    def generate_side_by_side_diff(self, original: str, modified: str,
                                   filepath: str, width: int = 80) -> str:
        """
        Generate a side-by-side diff view.

        Args:
            original: Original file content
            modified: Modified file content
            filepath: Path to the file (for display)
            width: Width of each column

        Returns:
            Side-by-side diff string
        """
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        diff = difflib.HtmlDiff().make_table(
            original_lines,
            modified_lines,
            fromdesc=f"Original: {filepath}",
            todesc=f"Modified: {filepath}",
            context=True,
            numlines=3
        )

        # Convert HTML table to plain text format
        # This is a simplified version - could be enhanced
        result = [f"\n{'='*120}"]
        result.append(f"File: {filepath}")
        result.append(f"{'='*120}\n")

        differ = difflib.Differ()
        diff_lines = list(differ.compare(original_lines, modified_lines))

        for line in diff_lines:
            if line.startswith('- '):
                result.append(f"\033[91m{line}\033[0m")  # Red for deletions
            elif line.startswith('+ '):
                result.append(f"\033[92m{line}\033[0m")  # Green for additions
            elif line.startswith('? '):
                continue  # Skip diff markers
            else:
                result.append(line)

        return '\n'.join(result)

    def get_file_backups(self, filepath: str) -> List[Tuple[str, datetime]]:
        """
        Get all backups for a specific file.

        Args:
            filepath: Path to the file

        Returns:
            List of (backup_path, timestamp) tuples
        """
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for backup_file in os.listdir(self.backup_dir):
            if backup_file.startswith(os.path.basename(filepath)):
                backup_path = os.path.join(self.backup_dir, backup_file)
                timestamp = datetime.fromtimestamp(os.path.getmtime(backup_path))
                backups.append((backup_path, timestamp))

        return sorted(backups, key=lambda x: x[1], reverse=True)

    def diff_with_backup(self, filepath: str, backup_index: int = 0,
                        diff_type: str = "unified") -> Optional[str]:
        """
        Generate diff between current file and a backup.

        Args:
            filepath: Path to the current file
            backup_index: Index of the backup to compare (0 = most recent)
            diff_type: Type of diff ("unified" or "side-by-side")

        Returns:
            Diff string or None if files not found
        """
        if not os.path.exists(filepath):
            return None

        backups = self.get_file_backups(filepath)
        if not backups or backup_index >= len(backups):
            return None

        backup_path = backups[backup_index][0]

        with open(filepath, 'r') as f:
            current_content = f.read()

        with open(backup_path, 'r') as f:
            backup_content = f.read()

        if diff_type == "unified":
            return self.generate_unified_diff(backup_content, current_content, filepath)
        else:
            return self.generate_side_by_side_diff(backup_content, current_content, filepath)

    def diff_files(self, file1: str, file2: str, diff_type: str = "unified") -> Optional[str]:
        """
        Generate diff between two arbitrary files.

        Args:
            file1: Path to first file
            file2: Path to second file
            diff_type: Type of diff ("unified" or "side-by-side")

        Returns:
            Diff string or None if files not found
        """
        if not os.path.exists(file1) or not os.path.exists(file2):
            return None

        with open(file1, 'r') as f:
            content1 = f.read()

        with open(file2, 'r') as f:
            content2 = f.read()

        if diff_type == "unified":
            return self.generate_unified_diff(content1, content2, file2)
        else:
            return self.generate_side_by_side_diff(content1, content2, file2)

    def preview_change(self, filepath: str, new_content: str,
                      diff_type: str = "unified") -> str:
        """
        Preview a proposed change to a file.

        Args:
            filepath: Path to the file
            new_content: Proposed new content
            diff_type: Type of diff ("unified" or "side-by-side")

        Returns:
            Diff string
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                original_content = f.read()
        else:
            original_content = ""

        if diff_type == "unified":
            return self.generate_unified_diff(original_content, new_content, filepath)
        else:
            return self.generate_side_by_side_diff(original_content, new_content, filepath)

    def format_diff_stats(self, diff_text: str) -> str:
        """
        Generate statistics from a unified diff.

        Args:
            diff_text: Unified diff text

        Returns:
            Formatted statistics string
        """
        lines = diff_text.split('\n')
        additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))

        return f"+{additions} -{deletions} lines changed"
