"""Diff utilities for viewing and managing file changes."""
import os
import difflib
import re
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .syntax_highlighter import SyntaxHighlighter, ColorScheme, ANSIColors


class DiffViewer:
    """Handle diff generation and viewing for file changes."""

    def __init__(self, agent_dir: str, theme: ColorScheme = ColorScheme.DARK,
                 enable_syntax_highlighting: bool = True):
        """
        Initialize the diff viewer.

        Args:
            agent_dir: Directory containing agent files
            theme: Color scheme for syntax highlighting
            enable_syntax_highlighting: Whether to enable syntax highlighting in diffs
        """
        self.agent_dir = agent_dir
        self.backup_dir = os.path.join(agent_dir, "backups")
        self.theme = theme
        self.enable_syntax_highlighting = enable_syntax_highlighting
        self.highlighter = SyntaxHighlighter(theme) if enable_syntax_highlighting else None

    def generate_unified_diff(self, original: str, modified: str,
                            filepath: str, context_lines: int = 3) -> str:
        """
        Generate a unified diff between original and modified content with syntax highlighting.

        Args:
            original: Original file content
            modified: Modified file content
            filepath: Path to the file (for display)
            context_lines: Number of context lines around changes

        Returns:
            Unified diff string with color coding
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

        diff_text = ''.join(diff)

        # Apply syntax highlighting to diff
        if self.enable_syntax_highlighting and self.highlighter:
            diff_text = self._highlight_unified_diff(diff_text, filepath)

        return diff_text

    def _highlight_unified_diff(self, diff_text: str, filepath: str) -> str:
        """
        Apply syntax highlighting to unified diff output.

        Args:
            diff_text: Raw unified diff text
            filepath: Path to the file (for language detection)

        Returns:
            Colorized diff text
        """
        lines = diff_text.split('\n')
        highlighted_lines = []
        language = self.highlighter.detect_language(filepath)

        for line in lines:
            if line.startswith('---') or line.startswith('+++'):
                # File headers in bold cyan
                highlighted_lines.append(
                    f"{ANSIColors.BOLD}{ANSIColors.BRIGHT_CYAN}{line}{ANSIColors.RESET}"
                )
            elif line.startswith('@@'):
                # Hunk headers in bold magenta
                highlighted_lines.append(
                    f"{ANSIColors.BOLD}{ANSIColors.BRIGHT_MAGENTA}{line}{ANSIColors.RESET}"
                )
            elif line.startswith('-'):
                # Deletions in red with syntax highlighting
                stripped = line[1:]  # Remove the '-' prefix
                if language and stripped.strip():
                    highlighted = self.highlighter.highlight(stripped, language)
                    highlighted_lines.append(
                        f"{ANSIColors.BRIGHT_RED}−{highlighted}{ANSIColors.RESET}"
                    )
                else:
                    highlighted_lines.append(f"{ANSIColors.BRIGHT_RED}{line}{ANSIColors.RESET}")
            elif line.startswith('+'):
                # Additions in green with syntax highlighting
                stripped = line[1:]  # Remove the '+' prefix
                if language and stripped.strip():
                    highlighted = self.highlighter.highlight(stripped, language)
                    highlighted_lines.append(
                        f"{ANSIColors.BRIGHT_GREEN}+{highlighted}{ANSIColors.RESET}"
                    )
                else:
                    highlighted_lines.append(f"{ANSIColors.BRIGHT_GREEN}{line}{ANSIColors.RESET}")
            else:
                # Context lines with syntax highlighting
                if language and line.strip():
                    highlighted = self.highlighter.highlight(line, language)
                    highlighted_lines.append(f"{ANSIColors.BRIGHT_BLACK} {highlighted}{ANSIColors.RESET}")
                else:
                    highlighted_lines.append(f"{ANSIColors.BRIGHT_BLACK}{line}{ANSIColors.RESET}")

        return '\n'.join(highlighted_lines)

    def generate_side_by_side_diff(self, original: str, modified: str,
                                   filepath: str, width: int = 80) -> str:
        """
        Generate a side-by-side diff view with syntax highlighting.

        Args:
            original: Original file content
            modified: Modified file content
            filepath: Path to the file (for display)
            width: Width of each column

        Returns:
            Side-by-side diff string with syntax highlighting
        """
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        # Build header
        result = [f"\n{ANSIColors.BOLD}{'='*120}{ANSIColors.RESET}"]
        result.append(f"{ANSIColors.BOLD}File: {ANSIColors.BRIGHT_CYAN}{filepath}{ANSIColors.RESET}")
        result.append(f"{ANSIColors.BOLD}{'='*120}{ANSIColors.RESET}\n")

        differ = difflib.Differ()
        diff_lines = list(differ.compare(original_lines, modified_lines))

        language = None
        if self.enable_syntax_highlighting and self.highlighter:
            language = self.highlighter.detect_language(filepath)

        for line in diff_lines:
            if line.startswith('- '):
                # Deletion - red with syntax highlighting
                content = line[2:]  # Remove '- ' prefix
                if language and content.strip():
                    highlighted = self.highlighter.highlight(content, language)
                    result.append(f"{ANSIColors.BRIGHT_RED}− {highlighted}{ANSIColors.RESET}")
                else:
                    result.append(f"{ANSIColors.BRIGHT_RED}− {content}{ANSIColors.RESET}")
            elif line.startswith('+ '):
                # Addition - green with syntax highlighting
                content = line[2:]  # Remove '+ ' prefix
                if language and content.strip():
                    highlighted = self.highlighter.highlight(content, language)
                    result.append(f"{ANSIColors.BRIGHT_GREEN}+ {highlighted}{ANSIColors.RESET}")
                else:
                    result.append(f"{ANSIColors.BRIGHT_GREEN}+ {content}{ANSIColors.RESET}")
            elif line.startswith('? '):
                # Skip diff markers
                continue
            else:
                # Context line with syntax highlighting
                content = line[2:] if len(line) > 2 else line
                if language and content.strip():
                    highlighted = self.highlighter.highlight(content, language)
                    result.append(f"{ANSIColors.BRIGHT_BLACK}  {highlighted}{ANSIColors.RESET}")
                else:
                    result.append(f"{ANSIColors.BRIGHT_BLACK}  {content}{ANSIColors.RESET}")

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
