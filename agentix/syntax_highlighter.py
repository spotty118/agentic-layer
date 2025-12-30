"""
Syntax Highlighter for Terminal IDE
Provides comprehensive syntax highlighting for multiple programming languages
using ANSI color codes for terminal display.
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class TokenType(Enum):
    """Token types for syntax highlighting."""
    KEYWORD = "keyword"
    STRING = "string"
    COMMENT = "comment"
    NUMBER = "number"
    FUNCTION = "function"
    CLASS = "class"
    OPERATOR = "operator"
    DECORATOR = "decorator"
    BUILTIN = "builtin"
    VARIABLE = "variable"
    TYPE = "type"
    CONSTANT = "constant"
    PROPERTY = "property"
    NAMESPACE = "namespace"
    PLAIN = "plain"


class ColorScheme(Enum):
    """Color schemes for different terminal themes."""
    DARK = "dark"
    LIGHT = "light"
    MONOKAI = "monokai"
    SOLARIZED = "solarized"
    DRACULA = "dracula"


class ANSIColors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 256 color support
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Generate 24-bit true color ANSI code."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def color_256(code: int) -> str:
        """Generate 256 color ANSI code."""
        return f"\033[38;5;{code}m"


class ColorTheme:
    """Color theme configuration for syntax highlighting."""

    THEMES = {
        ColorScheme.DARK: {
            TokenType.KEYWORD: ANSIColors.BRIGHT_MAGENTA,
            TokenType.STRING: ANSIColors.BRIGHT_GREEN,
            TokenType.COMMENT: ANSIColors.BRIGHT_BLACK,
            TokenType.NUMBER: ANSIColors.BRIGHT_CYAN,
            TokenType.FUNCTION: ANSIColors.BRIGHT_YELLOW,
            TokenType.CLASS: ANSIColors.BRIGHT_BLUE,
            TokenType.OPERATOR: ANSIColors.BRIGHT_RED,
            TokenType.DECORATOR: ANSIColors.BRIGHT_YELLOW,
            TokenType.BUILTIN: ANSIColors.CYAN,
            TokenType.VARIABLE: ANSIColors.WHITE,
            TokenType.TYPE: ANSIColors.BRIGHT_BLUE,
            TokenType.CONSTANT: ANSIColors.BRIGHT_CYAN,
            TokenType.PROPERTY: ANSIColors.BRIGHT_WHITE,
            TokenType.NAMESPACE: ANSIColors.BRIGHT_CYAN,
            TokenType.PLAIN: ANSIColors.WHITE,
        },
        ColorScheme.LIGHT: {
            TokenType.KEYWORD: ANSIColors.MAGENTA,
            TokenType.STRING: ANSIColors.GREEN,
            TokenType.COMMENT: ANSIColors.BRIGHT_BLACK,
            TokenType.NUMBER: ANSIColors.CYAN,
            TokenType.FUNCTION: ANSIColors.BLUE,
            TokenType.CLASS: ANSIColors.BLUE + ANSIColors.BOLD,
            TokenType.OPERATOR: ANSIColors.RED,
            TokenType.DECORATOR: ANSIColors.YELLOW,
            TokenType.BUILTIN: ANSIColors.CYAN,
            TokenType.VARIABLE: ANSIColors.BLACK,
            TokenType.TYPE: ANSIColors.BLUE,
            TokenType.CONSTANT: ANSIColors.CYAN,
            TokenType.PROPERTY: ANSIColors.BLACK,
            TokenType.NAMESPACE: ANSIColors.CYAN,
            TokenType.PLAIN: ANSIColors.BLACK,
        },
        ColorScheme.MONOKAI: {
            TokenType.KEYWORD: ANSIColors.rgb(249, 38, 114),  # Pink
            TokenType.STRING: ANSIColors.rgb(230, 219, 116),  # Yellow
            TokenType.COMMENT: ANSIColors.rgb(117, 113, 94),  # Gray
            TokenType.NUMBER: ANSIColors.rgb(174, 129, 255),  # Purple
            TokenType.FUNCTION: ANSIColors.rgb(166, 226, 46),  # Green
            TokenType.CLASS: ANSIColors.rgb(166, 226, 46),  # Green
            TokenType.OPERATOR: ANSIColors.rgb(249, 38, 114),  # Pink
            TokenType.DECORATOR: ANSIColors.rgb(102, 217, 239),  # Cyan
            TokenType.BUILTIN: ANSIColors.rgb(102, 217, 239),  # Cyan
            TokenType.VARIABLE: ANSIColors.rgb(248, 248, 242),  # White
            TokenType.TYPE: ANSIColors.rgb(102, 217, 239),  # Cyan
            TokenType.CONSTANT: ANSIColors.rgb(174, 129, 255),  # Purple
            TokenType.PROPERTY: ANSIColors.rgb(248, 248, 242),  # White
            TokenType.NAMESPACE: ANSIColors.rgb(102, 217, 239),  # Cyan
            TokenType.PLAIN: ANSIColors.rgb(248, 248, 242),  # White
        },
        ColorScheme.DRACULA: {
            TokenType.KEYWORD: ANSIColors.rgb(255, 121, 198),  # Pink
            TokenType.STRING: ANSIColors.rgb(241, 250, 140),  # Yellow
            TokenType.COMMENT: ANSIColors.rgb(98, 114, 164),  # Comment
            TokenType.NUMBER: ANSIColors.rgb(189, 147, 249),  # Purple
            TokenType.FUNCTION: ANSIColors.rgb(80, 250, 123),  # Green
            TokenType.CLASS: ANSIColors.rgb(139, 233, 253),  # Cyan
            TokenType.OPERATOR: ANSIColors.rgb(255, 121, 198),  # Pink
            TokenType.DECORATOR: ANSIColors.rgb(80, 250, 123),  # Green
            TokenType.BUILTIN: ANSIColors.rgb(139, 233, 253),  # Cyan
            TokenType.VARIABLE: ANSIColors.rgb(248, 248, 242),  # Foreground
            TokenType.TYPE: ANSIColors.rgb(139, 233, 253),  # Cyan
            TokenType.CONSTANT: ANSIColors.rgb(189, 147, 249),  # Purple
            TokenType.PROPERTY: ANSIColors.rgb(248, 248, 242),  # Foreground
            TokenType.NAMESPACE: ANSIColors.rgb(139, 233, 253),  # Cyan
            TokenType.PLAIN: ANSIColors.rgb(248, 248, 242),  # Foreground
        },
    }

    @classmethod
    def get_color(cls, token_type: TokenType, scheme: ColorScheme = ColorScheme.DARK) -> str:
        """Get ANSI color code for a token type in the specified theme."""
        return cls.THEMES.get(scheme, cls.THEMES[ColorScheme.DARK]).get(
            token_type, ANSIColors.WHITE
        )


class LanguageDefinition:
    """Language-specific syntax definitions."""

    PYTHON_KEYWORDS = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
        'try', 'while', 'with', 'yield'
    }

    PYTHON_BUILTINS = {
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
        'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
        'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
        'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
        'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
        'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
        'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
        'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
        'super', 'tuple', 'type', 'vars', 'zip', '__import__', 'self', 'cls'
    }

    JAVASCRIPT_KEYWORDS = {
        'async', 'await', 'break', 'case', 'catch', 'class', 'const',
        'continue', 'debugger', 'default', 'delete', 'do', 'else', 'export',
        'extends', 'finally', 'for', 'function', 'if', 'import', 'in',
        'instanceof', 'let', 'new', 'return', 'static', 'super', 'switch',
        'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with',
        'yield', 'enum', 'implements', 'interface', 'package', 'private',
        'protected', 'public', 'from', 'of'
    }

    JAVASCRIPT_BUILTINS = {
        'Array', 'Boolean', 'Date', 'Error', 'Function', 'JSON', 'Math',
        'Number', 'Object', 'Promise', 'RegExp', 'String', 'Symbol',
        'console', 'window', 'document', 'null', 'undefined', 'NaN',
        'Infinity', 'true', 'false'
    }

    GO_KEYWORDS = {
        'break', 'case', 'chan', 'const', 'continue', 'default', 'defer',
        'else', 'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import',
        'interface', 'map', 'package', 'range', 'return', 'select', 'struct',
        'switch', 'type', 'var'
    }

    GO_BUILTINS = {
        'append', 'bool', 'byte', 'cap', 'close', 'complex', 'complex64',
        'complex128', 'copy', 'delete', 'error', 'false', 'float32', 'float64',
        'imag', 'int', 'int8', 'int16', 'int32', 'int64', 'len', 'make',
        'new', 'nil', 'panic', 'print', 'println', 'real', 'recover',
        'rune', 'string', 'true', 'uint', 'uint8', 'uint16', 'uint32',
        'uint64', 'uintptr'
    }

    RUST_KEYWORDS = {
        'as', 'async', 'await', 'break', 'const', 'continue', 'crate', 'dyn',
        'else', 'enum', 'extern', 'false', 'fn', 'for', 'if', 'impl', 'in',
        'let', 'loop', 'match', 'mod', 'move', 'mut', 'pub', 'ref', 'return',
        'self', 'Self', 'static', 'struct', 'super', 'trait', 'true', 'type',
        'unsafe', 'use', 'where', 'while'
    }

    RUST_BUILTINS = {
        'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'i128',
        'isize', 'str', 'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
        'Box', 'String', 'Vec', 'Option', 'Result', 'Some', 'None',
        'Ok', 'Err', 'println', 'print', 'panic', 'assert', 'dbg'
    }

    SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE',
        'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW', 'JOIN', 'INNER', 'LEFT',
        'RIGHT', 'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN',
        'LIKE', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET',
        'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'NULL', 'IS',
        'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'DEFAULT',
        'AUTO_INCREMENT', 'VARCHAR', 'INT', 'FLOAT', 'DOUBLE', 'BOOLEAN',
        'DATE', 'DATETIME', 'TIMESTAMP', 'TEXT', 'BLOB'
    }

    @classmethod
    def get_keywords(cls, language: str) -> set:
        """Get keywords for a specific language."""
        keyword_map = {
            'python': cls.PYTHON_KEYWORDS,
            'javascript': cls.JAVASCRIPT_KEYWORDS,
            'typescript': cls.JAVASCRIPT_KEYWORDS,
            'go': cls.GO_KEYWORDS,
            'rust': cls.RUST_KEYWORDS,
            'sql': cls.SQL_KEYWORDS,
        }
        return keyword_map.get(language.lower(), set())

    @classmethod
    def get_builtins(cls, language: str) -> set:
        """Get built-in functions/types for a specific language."""
        builtin_map = {
            'python': cls.PYTHON_BUILTINS,
            'javascript': cls.JAVASCRIPT_BUILTINS,
            'typescript': cls.JAVASCRIPT_BUILTINS,
            'go': cls.GO_BUILTINS,
            'rust': cls.RUST_BUILTINS,
        }
        return builtin_map.get(language.lower(), set())


class SyntaxHighlighter:
    """
    Main syntax highlighter class.
    Tokenizes and colorizes source code for terminal display.
    """

    def __init__(self, theme: ColorScheme = ColorScheme.DARK):
        """Initialize the syntax highlighter with a color theme."""
        self.theme = theme
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rb': 'ruby',
            '.php': 'php',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',
            '.sql': 'sql',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
        }

    def detect_language(self, filename: str) -> Optional[str]:
        """Detect programming language from filename."""
        for ext, lang in self.language_map.items():
            if filename.lower().endswith(ext):
                return lang
        return None

    def highlight(self, code: str, language: Optional[str] = None) -> str:
        """
        Highlight source code with syntax coloring.

        Args:
            code: Source code to highlight
            language: Programming language (auto-detected if None)

        Returns:
            Colorized code with ANSI escape sequences
        """
        if not language:
            return code

        # Route to language-specific highlighter
        highlighter_map = {
            'python': self._highlight_python,
            'javascript': self._highlight_javascript,
            'typescript': self._highlight_javascript,
            'go': self._highlight_go,
            'rust': self._highlight_rust,
            'bash': self._highlight_bash,
            'sql': self._highlight_sql,
            'json': self._highlight_json,
            'yaml': self._highlight_yaml,
        }

        highlighter = highlighter_map.get(language.lower(), self._highlight_generic)
        return highlighter(code)

    def _colorize(self, text: str, token_type: TokenType) -> str:
        """Apply color to text based on token type."""
        color = ColorTheme.get_color(token_type, self.theme)
        return f"{color}{text}{ANSIColors.RESET}"

    def _highlight_python(self, code: str) -> str:
        """Highlight Python code."""
        lines = code.split('\n')
        highlighted_lines = []
        in_multiline_string = False
        multiline_delimiter = None

        for line in lines:
            if in_multiline_string:
                if multiline_delimiter in line:
                    # End of multiline string
                    parts = line.split(multiline_delimiter, 1)
                    highlighted_line = self._colorize(
                        parts[0] + multiline_delimiter, TokenType.STRING
                    )
                    if len(parts) > 1:
                        highlighted_line += self._highlight_python_line(parts[1])
                    in_multiline_string = False
                    multiline_delimiter = None
                else:
                    highlighted_line = self._colorize(line, TokenType.STRING)
                highlighted_lines.append(highlighted_line)
                continue

            # Check for multiline string start
            if '"""' in line or "'''" in line:
                if '"""' in line:
                    delimiter = '"""'
                else:
                    delimiter = "'''"

                parts = line.split(delimiter)
                if len(parts) >= 3:  # Complete multiline string on one line
                    highlighted_line = parts[0]
                    highlighted_line += self._colorize(
                        delimiter + parts[1] + delimiter, TokenType.STRING
                    )
                    if len(parts) > 2:
                        highlighted_line += self._highlight_python_line(parts[2])
                else:  # Start of multiline string
                    highlighted_line = self._highlight_python_line(parts[0])
                    highlighted_line += self._colorize(delimiter + parts[1], TokenType.STRING)
                    in_multiline_string = True
                    multiline_delimiter = delimiter
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(self._highlight_python_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_python_line(self, line: str) -> str:
        """Highlight a single line of Python code."""
        # Handle comments
        if '#' in line:
            parts = line.split('#', 1)
            return (
                self._highlight_python_tokens(parts[0]) +
                self._colorize('#' + parts[1], TokenType.COMMENT)
            )

        return self._highlight_python_tokens(line)

    def _highlight_python_tokens(self, line: str) -> str:
        """Tokenize and highlight Python code."""
        # Regex patterns
        string_pattern = r'(""".*?"""|\'\'\'.*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
        decorator_pattern = r'(@\w+)'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'
        function_pattern = r'\b(def)\s+(\w+)'
        class_pattern = r'\b(class)\s+(\w+)'
        word_pattern = r'\b(\w+)\b'

        result = line

        # Highlight strings first (to avoid highlighting keywords within strings)
        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        # Highlight decorators
        result = re.sub(
            decorator_pattern,
            lambda m: self._colorize(m.group(0), TokenType.DECORATOR),
            result
        )

        # Highlight function definitions
        result = re.sub(
            function_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.FUNCTION)
            ),
            result
        )

        # Highlight class definitions
        result = re.sub(
            class_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.CLASS)
            ),
            result
        )

        # Highlight numbers
        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        # Highlight keywords and builtins
        keywords = LanguageDefinition.get_keywords('python')
        builtins = LanguageDefinition.get_builtins('python')

        def highlight_word(match):
            word = match.group(0)
            if word in keywords:
                return self._colorize(word, TokenType.KEYWORD)
            elif word in builtins:
                return self._colorize(word, TokenType.BUILTIN)
            return word

        result = re.sub(word_pattern, highlight_word, result)

        # Restore strings
        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_javascript(self, code: str) -> str:
        """Highlight JavaScript/TypeScript code."""
        lines = code.split('\n')
        highlighted_lines = []
        in_multiline_comment = False

        for line in lines:
            if in_multiline_comment:
                if '*/' in line:
                    parts = line.split('*/', 1)
                    highlighted_line = self._colorize(parts[0] + '*/', TokenType.COMMENT)
                    if len(parts) > 1:
                        highlighted_line += self._highlight_javascript_line(parts[1])
                    in_multiline_comment = False
                else:
                    highlighted_line = self._colorize(line, TokenType.COMMENT)
                highlighted_lines.append(highlighted_line)
                continue

            # Check for multiline comment start
            if '/*' in line:
                parts = line.split('/*', 1)
                if '*/' in parts[1]:
                    inner_parts = parts[1].split('*/', 1)
                    highlighted_line = self._highlight_javascript_line(parts[0])
                    highlighted_line += self._colorize('/*' + inner_parts[0] + '*/', TokenType.COMMENT)
                    highlighted_line += self._highlight_javascript_line(inner_parts[1])
                else:
                    highlighted_line = self._highlight_javascript_line(parts[0])
                    highlighted_line += self._colorize('/*' + parts[1], TokenType.COMMENT)
                    in_multiline_comment = True
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(self._highlight_javascript_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_javascript_line(self, line: str) -> str:
        """Highlight a single line of JavaScript code."""
        # Handle single-line comments
        if '//' in line:
            parts = line.split('//', 1)
            return (
                self._highlight_javascript_tokens(parts[0]) +
                self._colorize('//' + parts[1], TokenType.COMMENT)
            )

        return self._highlight_javascript_tokens(line)

    def _highlight_javascript_tokens(self, line: str) -> str:
        """Tokenize and highlight JavaScript code."""
        string_pattern = r'(`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'
        function_pattern = r'\b(function|async\s+function)\s+(\w+)'
        class_pattern = r'\b(class)\s+(\w+)'
        word_pattern = r'\b(\w+)\b'

        result = line

        # Highlight strings
        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        # Highlight function definitions
        result = re.sub(
            function_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.FUNCTION)
            ),
            result
        )

        # Highlight class definitions
        result = re.sub(
            class_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.CLASS)
            ),
            result
        )

        # Highlight numbers
        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        # Highlight keywords and builtins
        keywords = LanguageDefinition.get_keywords('javascript')
        builtins = LanguageDefinition.get_builtins('javascript')

        def highlight_word(match):
            word = match.group(0)
            if word in keywords:
                return self._colorize(word, TokenType.KEYWORD)
            elif word in builtins:
                return self._colorize(word, TokenType.BUILTIN)
            return word

        result = re.sub(word_pattern, highlight_word, result)

        # Restore strings
        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_go(self, code: str) -> str:
        """Highlight Go code."""
        lines = code.split('\n')
        highlighted_lines = []
        in_multiline_comment = False

        for line in lines:
            if in_multiline_comment:
                if '*/' in line:
                    parts = line.split('*/', 1)
                    highlighted_line = self._colorize(parts[0] + '*/', TokenType.COMMENT)
                    if len(parts) > 1:
                        highlighted_line += self._highlight_go_line(parts[1])
                    in_multiline_comment = False
                else:
                    highlighted_line = self._colorize(line, TokenType.COMMENT)
                highlighted_lines.append(highlighted_line)
                continue

            if '/*' in line:
                parts = line.split('/*', 1)
                if '*/' in parts[1]:
                    inner_parts = parts[1].split('*/', 1)
                    highlighted_line = self._highlight_go_line(parts[0])
                    highlighted_line += self._colorize('/*' + inner_parts[0] + '*/', TokenType.COMMENT)
                    highlighted_line += self._highlight_go_line(inner_parts[1])
                else:
                    highlighted_line = self._highlight_go_line(parts[0])
                    highlighted_line += self._colorize('/*' + parts[1], TokenType.COMMENT)
                    in_multiline_comment = True
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(self._highlight_go_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_go_line(self, line: str) -> str:
        """Highlight a single line of Go code."""
        if '//' in line:
            parts = line.split('//', 1)
            return (
                self._highlight_go_tokens(parts[0]) +
                self._colorize('//' + parts[1], TokenType.COMMENT)
            )
        return self._highlight_go_tokens(line)

    def _highlight_go_tokens(self, line: str) -> str:
        """Tokenize and highlight Go code."""
        string_pattern = r'(`[^`]*`|"(?:[^"\\]|\\.)*")'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'
        function_pattern = r'\b(func)\s+(\w+)'
        word_pattern = r'\b(\w+)\b'

        result = line

        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        result = re.sub(
            function_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.FUNCTION)
            ),
            result
        )

        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        keywords = LanguageDefinition.get_keywords('go')
        builtins = LanguageDefinition.get_builtins('go')

        def highlight_word(match):
            word = match.group(0)
            if word in keywords:
                return self._colorize(word, TokenType.KEYWORD)
            elif word in builtins:
                return self._colorize(word, TokenType.BUILTIN)
            return word

        result = re.sub(word_pattern, highlight_word, result)

        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_rust(self, code: str) -> str:
        """Highlight Rust code."""
        lines = code.split('\n')
        highlighted_lines = []
        in_multiline_comment = False

        for line in lines:
            if in_multiline_comment:
                if '*/' in line:
                    parts = line.split('*/', 1)
                    highlighted_line = self._colorize(parts[0] + '*/', TokenType.COMMENT)
                    if len(parts) > 1:
                        highlighted_line += self._highlight_rust_line(parts[1])
                    in_multiline_comment = False
                else:
                    highlighted_line = self._colorize(line, TokenType.COMMENT)
                highlighted_lines.append(highlighted_line)
                continue

            if '/*' in line:
                parts = line.split('/*', 1)
                if '*/' in parts[1]:
                    inner_parts = parts[1].split('*/', 1)
                    highlighted_line = self._highlight_rust_line(parts[0])
                    highlighted_line += self._colorize('/*' + inner_parts[0] + '*/', TokenType.COMMENT)
                    highlighted_line += self._highlight_rust_line(inner_parts[1])
                else:
                    highlighted_line = self._highlight_rust_line(parts[0])
                    highlighted_line += self._colorize('/*' + parts[1], TokenType.COMMENT)
                    in_multiline_comment = True
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(self._highlight_rust_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_rust_line(self, line: str) -> str:
        """Highlight a single line of Rust code."""
        if '//' in line:
            parts = line.split('//', 1)
            return (
                self._highlight_rust_tokens(parts[0]) +
                self._colorize('//' + parts[1], TokenType.COMMENT)
            )
        return self._highlight_rust_tokens(line)

    def _highlight_rust_tokens(self, line: str) -> str:
        """Tokenize and highlight Rust code."""
        string_pattern = r'("(?:[^"\\]|\\.)*")'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'
        function_pattern = r'\b(fn)\s+(\w+)'
        macro_pattern = r'(\w+!)'
        word_pattern = r'\b(\w+)\b'

        result = line

        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        result = re.sub(
            macro_pattern,
            lambda m: self._colorize(m.group(0), TokenType.FUNCTION),
            result
        )

        result = re.sub(
            function_pattern,
            lambda m: (
                self._colorize(m.group(1), TokenType.KEYWORD) + ' ' +
                self._colorize(m.group(2), TokenType.FUNCTION)
            ),
            result
        )

        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        keywords = LanguageDefinition.get_keywords('rust')
        builtins = LanguageDefinition.get_builtins('rust')

        def highlight_word(match):
            word = match.group(0)
            if word in keywords:
                return self._colorize(word, TokenType.KEYWORD)
            elif word in builtins:
                return self._colorize(word, TokenType.BUILTIN)
            return word

        result = re.sub(word_pattern, highlight_word, result)

        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_bash(self, code: str) -> str:
        """Highlight Bash/Shell code."""
        lines = code.split('\n')
        highlighted_lines = []

        for line in lines:
            if line.strip().startswith('#'):
                highlighted_lines.append(self._colorize(line, TokenType.COMMENT))
            else:
                highlighted_lines.append(self._highlight_bash_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_bash_line(self, line: str) -> str:
        """Highlight a single line of Bash code."""
        if '#' in line:
            parts = line.split('#', 1)
            return (
                self._highlight_bash_tokens(parts[0]) +
                self._colorize('#' + parts[1], TokenType.COMMENT)
            )
        return self._highlight_bash_tokens(line)

    def _highlight_bash_tokens(self, line: str) -> str:
        """Tokenize and highlight Bash code."""
        string_pattern = r'("(?:[^"\\]|\\.)*"|\'[^\']*\')'
        variable_pattern = r'(\$\{?\w+\}?)'
        keyword_pattern = r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|function)\b'

        result = line

        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        result = re.sub(
            variable_pattern,
            lambda m: self._colorize(m.group(0), TokenType.VARIABLE),
            result
        )

        result = re.sub(
            keyword_pattern,
            lambda m: self._colorize(m.group(0), TokenType.KEYWORD),
            result
        )

        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_sql(self, code: str) -> str:
        """Highlight SQL code."""
        lines = code.split('\n')
        highlighted_lines = []

        for line in lines:
            if line.strip().startswith('--'):
                highlighted_lines.append(self._colorize(line, TokenType.COMMENT))
            else:
                highlighted_lines.append(self._highlight_sql_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_sql_line(self, line: str) -> str:
        """Highlight a single line of SQL code."""
        if '--' in line:
            parts = line.split('--', 1)
            return (
                self._highlight_sql_tokens(parts[0]) +
                self._colorize('--' + parts[1], TokenType.COMMENT)
            )
        return self._highlight_sql_tokens(line)

    def _highlight_sql_tokens(self, line: str) -> str:
        """Tokenize and highlight SQL code."""
        string_pattern = r'(\'(?:[^\'\\]|\\.)*\')'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'

        result = line

        strings = []
        for match in re.finditer(string_pattern, line):
            placeholder = f"__STRING_{len(strings)}__"
            strings.append(self._colorize(match.group(0), TokenType.STRING))
            result = result.replace(match.group(0), placeholder, 1)

        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        keywords = LanguageDefinition.get_keywords('sql')
        word_pattern = r'\b(\w+)\b'

        def highlight_word(match):
            word = match.group(0)
            if word.upper() in keywords:
                return self._colorize(word, TokenType.KEYWORD)
            return word

        result = re.sub(word_pattern, highlight_word, result)

        for i, string in enumerate(strings):
            result = result.replace(f"__STRING_{i}__", string, 1)

        return result

    def _highlight_json(self, code: str) -> str:
        """Highlight JSON code."""
        key_pattern = r'("[\w\s\-\_]+")(\s*:)'
        string_pattern = r':\s*("(?:[^"\\]|\\.)*")'
        number_pattern = r':\s*(\d+\.?\d*|\.\d+)'
        boolean_pattern = r':\s*(true|false|null)'

        result = code

        result = re.sub(
            key_pattern,
            lambda m: self._colorize(m.group(1), TokenType.PROPERTY) + m.group(2),
            result
        )

        result = re.sub(
            string_pattern,
            lambda m: ': ' + self._colorize(m.group(1), TokenType.STRING),
            result
        )

        result = re.sub(
            number_pattern,
            lambda m: ': ' + self._colorize(m.group(1), TokenType.NUMBER),
            result
        )

        result = re.sub(
            boolean_pattern,
            lambda m: ': ' + self._colorize(m.group(1), TokenType.KEYWORD),
            result
        )

        return result

    def _highlight_yaml(self, code: str) -> str:
        """Highlight YAML code."""
        lines = code.split('\n')
        highlighted_lines = []

        for line in lines:
            if line.strip().startswith('#'):
                highlighted_lines.append(self._colorize(line, TokenType.COMMENT))
            else:
                highlighted_lines.append(self._highlight_yaml_line(line))

        return '\n'.join(highlighted_lines)

    def _highlight_yaml_line(self, line: str) -> str:
        """Highlight a single line of YAML code."""
        if '#' in line:
            parts = line.split('#', 1)
            return (
                self._highlight_yaml_tokens(parts[0]) +
                self._colorize('#' + parts[1], TokenType.COMMENT)
            )
        return self._highlight_yaml_tokens(line)

    def _highlight_yaml_tokens(self, line: str) -> str:
        """Tokenize and highlight YAML code."""
        key_pattern = r'^(\s*)(\w[\w\s\-]*):(.*)$'
        string_pattern = r'(\'[^\']*\'|"(?:[^"\\]|\\.)*")'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'
        boolean_pattern = r'\b(true|false|yes|no|null)\b'

        match = re.match(key_pattern, line)
        if match:
            indent = match.group(1)
            key = match.group(2)
            rest = match.group(3)

            result = indent + self._colorize(key, TokenType.PROPERTY) + ':' + rest

            result = re.sub(
                string_pattern,
                lambda m: self._colorize(m.group(0), TokenType.STRING),
                result
            )

            result = re.sub(
                number_pattern,
                lambda m: self._colorize(m.group(0), TokenType.NUMBER),
                result
            )

            result = re.sub(
                boolean_pattern,
                lambda m: self._colorize(m.group(0), TokenType.KEYWORD),
                result
            )

            return result

        return line

    def _highlight_generic(self, code: str) -> str:
        """Generic highlighting for unknown languages."""
        string_pattern = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
        number_pattern = r'\b(\d+\.?\d*|\.\d+)\b'

        result = code

        result = re.sub(
            string_pattern,
            lambda m: self._colorize(m.group(0), TokenType.STRING),
            result
        )

        result = re.sub(
            number_pattern,
            lambda m: self._colorize(m.group(0), TokenType.NUMBER),
            result
        )

        return result


# Convenience function for quick highlighting
def highlight_code(code: str, language: Optional[str] = None,
                   theme: ColorScheme = ColorScheme.DARK) -> str:
    """
    Quick function to highlight code.

    Args:
        code: Source code to highlight
        language: Programming language (optional)
        theme: Color theme to use

    Returns:
        Colorized code with ANSI escape sequences
    """
    highlighter = SyntaxHighlighter(theme)
    return highlighter.highlight(code, language)
