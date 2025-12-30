"""
Code Viewer for Terminal IDE
Provides IDE-like code viewing capabilities with syntax highlighting,
line numbers, and various display options.
"""

import os
from typing import Optional, List, Tuple
from pathlib import Path

from .syntax_highlighter import (
    SyntaxHighlighter,
    ColorScheme,
    ANSIColors,
)


class CodeViewer:
    """
    Terminal-based code viewer with IDE-like features.
    Displays code with syntax highlighting, line numbers, and formatting.
    """

    def __init__(self, theme: ColorScheme = ColorScheme.DARK, tab_width: int = 4):
        """
        Initialize the code viewer.

        Args:
            theme: Color scheme to use for syntax highlighting
            tab_width: Number of spaces to use for tab expansion
        """
        self.highlighter = SyntaxHighlighter(theme)
        self.theme = theme
        self.tab_width = tab_width

    def view_file(
        self,
        file_path: str,
        show_line_numbers: bool = True,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        highlight_lines: Optional[List[int]] = None,
        context_lines: int = 0,
    ) -> str:
        """
        View a file with syntax highlighting.

        Args:
            file_path: Path to the file to view
            show_line_numbers: Whether to show line numbers
            start_line: Starting line number (1-indexed, inclusive)
            end_line: Ending line number (1-indexed, inclusive)
            highlight_lines: List of line numbers to highlight
            context_lines: Number of context lines to show around highlighted lines

        Returns:
            Formatted and highlighted code
        """
        if not os.path.exists(file_path):
            return f"{ANSIColors.BRIGHT_RED}Error: File not found: {file_path}{ANSIColors.RESET}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try to read as binary file (images, etc.)
            return f"{ANSIColors.BRIGHT_YELLOW}Warning: Binary file, cannot display{ANSIColors.RESET}"
        except Exception as e:
            return f"{ANSIColors.BRIGHT_RED}Error reading file: {str(e)}{ANSIColors.RESET}"

        # Detect language
        language = self.highlighter.detect_language(file_path)

        # Expand tabs
        lines = [line.replace('\t', ' ' * self.tab_width) for line in lines]

        # Determine line range
        total_lines = len(lines)
        start = (start_line - 1) if start_line else 0
        end = end_line if end_line else total_lines

        # Adjust for context lines
        if highlight_lines and context_lines > 0:
            expanded_range = set()
            for line_num in highlight_lines:
                for i in range(
                    max(1, line_num - context_lines),
                    min(total_lines + 1, line_num + context_lines + 1)
                ):
                    expanded_range.add(i)

            if expanded_range:
                start = min(expanded_range) - 1
                end = max(expanded_range)

        # Clamp to valid range
        start = max(0, min(start, total_lines))
        end = max(0, min(end, total_lines))

        # Extract lines to display
        display_lines = lines[start:end]

        # Highlight the code
        if language:
            code_text = ''.join(display_lines)
            highlighted_code = self.highlighter.highlight(code_text, language)
            display_lines = highlighted_code.split('\n')

        # Format with line numbers
        if show_line_numbers:
            return self._format_with_line_numbers(
                display_lines,
                start_line=start + 1,
                highlight_lines=highlight_lines
            )
        else:
            return '\n'.join(display_lines)

    def _format_with_line_numbers(
        self,
        lines: List[str],
        start_line: int = 1,
        highlight_lines: Optional[List[int]] = None
    ) -> str:
        """
        Format lines with line numbers.

        Args:
            lines: Lines of code
            start_line: Starting line number
            highlight_lines: Line numbers to highlight

        Returns:
            Formatted code with line numbers
        """
        if not lines:
            return ""

        highlight_set = set(highlight_lines) if highlight_lines else set()

        # Calculate max line number width
        max_line_num = start_line + len(lines) - 1
        line_num_width = len(str(max_line_num))

        formatted_lines = []
        for idx, line in enumerate(lines):
            line_num = start_line + idx
            is_highlighted = line_num in highlight_set

            # Create line number prefix
            line_num_str = str(line_num).rjust(line_num_width)

            if is_highlighted:
                # Highlight the line number and add indicator
                line_num_prefix = (
                    f"{ANSIColors.BRIGHT_YELLOW}{line_num_str} ▶ {ANSIColors.RESET}"
                )
                # Add background highlight to the line
                line_content = f"{ANSIColors.rgb(60, 60, 40)}{line}{ANSIColors.RESET}"
            else:
                # Regular line number
                line_num_prefix = f"{ANSIColors.BRIGHT_BLACK}{line_num_str} │ {ANSIColors.RESET}"
                line_content = line

            formatted_lines.append(f"{line_num_prefix}{line_content}")

        return '\n'.join(formatted_lines)

    def view_snippet(
        self,
        code: str,
        language: Optional[str] = None,
        show_line_numbers: bool = True,
        start_line: int = 1,
    ) -> str:
        """
        View a code snippet with syntax highlighting.

        Args:
            code: Code snippet to view
            language: Programming language
            show_line_numbers: Whether to show line numbers
            start_line: Starting line number

        Returns:
            Formatted and highlighted code snippet
        """
        # Expand tabs
        code = code.replace('\t', ' ' * self.tab_width)

        # Highlight the code
        if language:
            highlighted_code = self.highlighter.highlight(code, language)
        else:
            highlighted_code = code

        lines = highlighted_code.split('\n')

        # Format with line numbers if requested
        if show_line_numbers:
            return self._format_with_line_numbers(lines, start_line=start_line)
        else:
            return highlighted_code

    def compare_files(
        self,
        file1: str,
        file2: str,
        show_line_numbers: bool = True
    ) -> str:
        """
        Display two files side by side for comparison.

        Args:
            file1: Path to first file
            file2: Path to second file
            show_line_numbers: Whether to show line numbers

        Returns:
            Side-by-side comparison
        """
        # Read both files
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                lines1 = f.readlines()
        except Exception as e:
            return f"{ANSIColors.BRIGHT_RED}Error reading {file1}: {str(e)}{ANSIColors.RESET}"

        try:
            with open(file2, 'r', encoding='utf-8') as f:
                lines2 = f.readlines()
        except Exception as e:
            return f"{ANSIColors.BRIGHT_RED}Error reading {file2}: {str(e)}{ANSIColors.RESET}"

        # Detect language (use first file's extension)
        language = self.highlighter.detect_language(file1)

        # Highlight both files
        if language:
            code1 = ''.join(lines1)
            code2 = ''.join(lines2)
            highlighted1 = self.highlighter.highlight(code1, language).split('\n')
            highlighted2 = self.highlighter.highlight(code2, language).split('\n')
        else:
            highlighted1 = [line.rstrip('\n') for line in lines1]
            highlighted2 = [line.rstrip('\n') for line in lines2]

        # Create side-by-side display
        max_lines = max(len(highlighted1), len(highlighted2))
        max_width = 80  # Half screen width

        # Pad shorter file
        while len(highlighted1) < max_lines:
            highlighted1.append('')
        while len(highlighted2) < max_lines:
            highlighted2.append('')

        # Build comparison
        result = []

        # Header
        header = (
            f"{ANSIColors.BOLD}{file1:^{max_width}}{ANSIColors.RESET} │ "
            f"{ANSIColors.BOLD}{file2:^{max_width}}{ANSIColors.RESET}"
        )
        result.append(header)
        result.append("─" * max_width + "┼" + "─" * max_width)

        # Line by line comparison
        for i in range(max_lines):
            left = highlighted1[i][:max_width].ljust(max_width)
            right = highlighted2[i][:max_width].ljust(max_width)

            if show_line_numbers:
                line_num = str(i + 1).rjust(4)
                left_prefix = f"{ANSIColors.BRIGHT_BLACK}{line_num} │ {ANSIColors.RESET}"
                right_prefix = f"{ANSIColors.BRIGHT_BLACK}{line_num} │ {ANSIColors.RESET}"
                result.append(f"{left_prefix}{left} │ {right_prefix}{right}")
            else:
                result.append(f"{left} │ {right}")

        return '\n'.join(result)

    def show_file_info(self, file_path: str) -> str:
        """
        Display file information and statistics.

        Args:
            file_path: Path to the file

        Returns:
            Formatted file information
        """
        if not os.path.exists(file_path):
            return f"{ANSIColors.BRIGHT_RED}Error: File not found: {file_path}{ANSIColors.RESET}"

        try:
            # Get file stats
            stat = os.stat(file_path)
            file_size = stat.st_size

            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            non_empty_lines = sum(1 for line in lines if line.strip())

            # Count comment lines (basic heuristic)
            comment_lines = 0
            language = self.highlighter.detect_language(file_path)
            if language in ['python']:
                comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            elif language in ['javascript', 'typescript', 'go', 'rust', 'java', 'c', 'cpp']:
                comment_lines = sum(1 for line in lines if line.strip().startswith('//'))

            code_lines = non_empty_lines - comment_lines

            # Format size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            # Build info display
            info = []
            info.append(f"{ANSIColors.BOLD}File Information{ANSIColors.RESET}")
            info.append(f"{'─' * 50}")
            info.append(f"Path:          {ANSIColors.BRIGHT_CYAN}{file_path}{ANSIColors.RESET}")
            info.append(f"Language:      {ANSIColors.BRIGHT_YELLOW}{language or 'Unknown'}{ANSIColors.RESET}")
            info.append(f"Size:          {ANSIColors.BRIGHT_GREEN}{size_str}{ANSIColors.RESET}")
            info.append(f"Total Lines:   {ANSIColors.BRIGHT_WHITE}{total_lines}{ANSIColors.RESET}")
            info.append(f"Code Lines:    {ANSIColors.BRIGHT_WHITE}{code_lines}{ANSIColors.RESET}")
            info.append(f"Comment Lines: {ANSIColors.BRIGHT_BLACK}{comment_lines}{ANSIColors.RESET}")
            info.append(f"Empty Lines:   {ANSIColors.BRIGHT_BLACK}{total_lines - non_empty_lines}{ANSIColors.RESET}")

            return '\n'.join(info)

        except UnicodeDecodeError:
            return f"{ANSIColors.BRIGHT_YELLOW}Binary file{ANSIColors.RESET}"
        except Exception as e:
            return f"{ANSIColors.BRIGHT_RED}Error: {str(e)}{ANSIColors.RESET}"

    def search_in_file(
        self,
        file_path: str,
        search_term: str,
        context_lines: int = 2,
        case_sensitive: bool = False
    ) -> str:
        """
        Search for a term in a file and display results with context.

        Args:
            file_path: Path to the file to search
            search_term: Term to search for
            context_lines: Number of context lines to show around matches
            case_sensitive: Whether the search should be case-sensitive

        Returns:
            Formatted search results with context
        """
        if not os.path.exists(file_path):
            return f"{ANSIColors.BRIGHT_RED}Error: File not found: {file_path}{ANSIColors.RESET}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return f"{ANSIColors.BRIGHT_RED}Error reading file: {str(e)}{ANSIColors.RESET}"

        # Find matching lines
        matches = []
        search_lower = search_term.lower() if not case_sensitive else search_term

        for i, line in enumerate(lines):
            line_to_search = line if case_sensitive else line.lower()
            if search_lower in line_to_search:
                matches.append(i + 1)  # 1-indexed

        if not matches:
            return (
                f"{ANSIColors.BRIGHT_YELLOW}No matches found for "
                f"'{search_term}' in {file_path}{ANSIColors.RESET}"
            )

        # Display results
        result = []
        result.append(
            f"{ANSIColors.BOLD}Found {len(matches)} match(es) for "
            f"'{ANSIColors.BRIGHT_CYAN}{search_term}{ANSIColors.RESET}{ANSIColors.BOLD}' "
            f"in {file_path}{ANSIColors.RESET}"
        )
        result.append("─" * 80)
        result.append("")

        # View file with highlighted matches
        highlighted_view = self.view_file(
            file_path,
            show_line_numbers=True,
            highlight_lines=matches,
            context_lines=context_lines
        )

        result.append(highlighted_view)
        return '\n'.join(result)


def view_code_file(
    file_path: str,
    theme: ColorScheme = ColorScheme.DARK,
    show_line_numbers: bool = True,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> str:
    """
    Convenience function to view a code file.

    Args:
        file_path: Path to the file to view
        theme: Color scheme to use
        show_line_numbers: Whether to show line numbers
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)

    Returns:
        Formatted and highlighted code
    """
    viewer = CodeViewer(theme)
    return viewer.view_file(
        file_path,
        show_line_numbers=show_line_numbers,
        start_line=start_line,
        end_line=end_line
    )


def view_code_snippet(
    code: str,
    language: Optional[str] = None,
    theme: ColorScheme = ColorScheme.DARK,
    show_line_numbers: bool = True
) -> str:
    """
    Convenience function to view a code snippet.

    Args:
        code: Code snippet to view
        language: Programming language
        theme: Color scheme to use
        show_line_numbers: Whether to show line numbers

    Returns:
        Formatted and highlighted code snippet
    """
    viewer = CodeViewer(theme)
    return viewer.view_snippet(
        code,
        language=language,
        show_line_numbers=show_line_numbers
    )
