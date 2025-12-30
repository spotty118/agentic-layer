# Syntax Highlighting Features

Agentix now includes comprehensive syntax highlighting capabilities for viewing code in the terminal, similar to native IDEs like VS Code, Claude Code, Gemini, and Codex.

## Features

### 🎨 Multi-Language Support

The syntax highlighter supports the following programming languages:

- **Python** - Full syntax highlighting with keywords, strings, comments, decorators, functions, classes
- **JavaScript/TypeScript** - Modern JS/TS syntax with async/await, classes, template literals
- **Go** - Complete Go syntax support
- **Rust** - Rust syntax with macros, types, and patterns
- **Java/C/C++** - C-family language support
- **Shell/Bash** - Shell script highlighting
- **SQL** - Database query highlighting
- **JSON** - Structured data highlighting
- **YAML** - Configuration file highlighting
- **HTML/CSS** - Web markup and styling
- **Markdown** - Documentation highlighting

### 🌈 Color Schemes

Multiple color themes are available:

1. **Dark Theme** (Default) - Optimized for dark terminals
2. **Light Theme** - For light-colored terminals
3. **Monokai** - Popular Sublime Text theme
4. **Dracula** - Modern dark theme with vibrant colors

### 🔧 Token Types

The highlighter recognizes and colors different code elements:

- **Keywords** - Language keywords (if, for, class, def, etc.)
- **Strings** - String literals with quotes
- **Comments** - Single-line and multi-line comments
- **Numbers** - Numeric literals
- **Functions** - Function definitions and calls
- **Classes** - Class definitions
- **Operators** - Mathematical and logical operators
- **Decorators** - Python decorators and annotations
- **Builtins** - Built-in functions and types
- **Variables** - Variable names
- **Types** - Type annotations
- **Constants** - Constant values

## Command Line Usage

### View Files with Syntax Highlighting

```bash
# View a file
agentix view filename.py

# View with different theme
agentix view filename.js --theme monokai

# View specific line range
agentix view filename.py --start 10 --end 50

# Hide line numbers
agentix view filename.py --no-line-numbers

# Show file information and statistics
agentix view filename.py --info

# Search within a file
agentix view filename.py --search "function_name" --context 3
```

### Enhanced Diff Viewing

Diffs now include syntax highlighting for better readability:

```bash
# View diff with syntax highlighting
agentix diff filename.py

# Compare two files with highlighting
agentix diff filename.py --compare other_file.py

# Side-by-side diff with syntax highlighting
agentix diff filename.py --type side-by-side
```

## Python API Usage

### Basic Syntax Highlighting

```python
from agentix import SyntaxHighlighter, ColorScheme

# Create highlighter
highlighter = SyntaxHighlighter(theme=ColorScheme.DARK)

# Highlight code
code = '''
def hello_world():
    print("Hello, World!")
'''

highlighted = highlighter.highlight(code, language='python')
print(highlighted)
```

### Code Viewer

```python
from agentix import CodeViewer, ColorScheme

# Create viewer
viewer = CodeViewer(theme=ColorScheme.MONOKAI)

# View file with line numbers
output = viewer.view_file(
    'example.py',
    show_line_numbers=True,
    start_line=1,
    end_line=50
)
print(output)

# Search in file
results = viewer.search_in_file(
    'example.py',
    search_term='def',
    context_lines=2
)
print(results)

# Show file info
info = viewer.show_file_info('example.py')
print(info)
```

### Enhanced Diff Viewer

```python
from agentix import DiffViewer, ColorScheme

# Create diff viewer with syntax highlighting
diff_viewer = DiffViewer(
    agent_dir='.agent',
    theme=ColorScheme.DRACULA,
    enable_syntax_highlighting=True
)

# Generate unified diff with syntax highlighting
diff = diff_viewer.generate_unified_diff(
    original_content,
    modified_content,
    filepath='example.py'
)
print(diff)
```

## Architecture

### Core Components

#### SyntaxHighlighter (`agentix/syntax_highlighter.py`)

The main syntax highlighting engine that:
- Tokenizes source code by language
- Applies ANSI color codes to tokens
- Supports multiple color schemes
- Handles language-specific syntax rules

#### CodeViewer (`agentix/code_viewer.py`)

Terminal-based code viewer that:
- Displays files with syntax highlighting
- Shows line numbers
- Supports line ranges
- Provides search functionality
- Shows file statistics

#### DiffViewer (`agentix/diff_utils.py`)

Enhanced diff viewer with:
- Syntax highlighted diffs
- Unified and side-by-side views
- Color-coded additions/deletions
- Backup comparison support

## Color Coding

### Dark Theme Color Mappings

| Token Type | Color | ANSI Code |
|------------|-------|-----------|
| Keywords | Bright Magenta | `\033[95m` |
| Strings | Bright Green | `\033[92m` |
| Comments | Bright Black (Gray) | `\033[90m` |
| Numbers | Bright Cyan | `\033[96m` |
| Functions | Bright Yellow | `\033[93m` |
| Classes | Bright Blue | `\033[94m` |
| Operators | Bright Red | `\033[91m` |
| Builtins | Cyan | `\033[36m` |

### Advanced Themes

Monokai and Dracula themes use 24-bit true color (RGB) for more accurate colors:

```python
# Monokai pink for keywords
ANSIColors.rgb(249, 38, 114)

# Dracula purple for numbers
ANSIColors.rgb(189, 147, 249)
```

## Examples

### Python Example

```python
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n

    # Use dynamic programming
    fib = [0, 1]
    for i in range(2, n + 1):
        fib.append(fib[i-1] + fib[i-2])

    return fib[n]
```

Colors:
- `def`, `return`, `if`, `for`, `in` - Magenta (keywords)
- `"""Calculate..."""` - Green (string)
- `# Use dynamic...` - Gray (comment)
- `0`, `1`, `2` - Cyan (numbers)
- `calculate_fibonacci` - Yellow (function)
- `int`, `range`, `append` - Cyan (builtins/types)

### JavaScript Example

```javascript
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching user:", error);
        return null;
    }
}
```

Colors:
- `async`, `function`, `try`, `catch`, `return`, `const`, `await` - Magenta
- `` `/api/users/${userId}` ``, `"Error fetching user:"` - Green
- `// Comments` - Gray
- `fetchUserData` - Yellow (function name)
- `console`, `null` - Cyan (builtins)

## Terminal Compatibility

### ANSI Color Support

The syntax highlighter uses ANSI escape codes that work in most modern terminals:

- ✅ Linux terminals (GNOME Terminal, Konsole, etc.)
- ✅ macOS Terminal and iTerm2
- ✅ Windows Terminal
- ✅ VS Code integrated terminal
- ✅ SSH sessions with color support
- ⚠️  Windows Command Prompt (limited color support)

### True Color (24-bit) Support

Monokai and Dracula themes use RGB colors. These require terminals with true color support:

- ✅ iTerm2 (macOS)
- ✅ GNOME Terminal 3.16+
- ✅ Konsole (KDE)
- ✅ Windows Terminal
- ✅ VS Code terminal
- ❌ Basic terminals (will show garbled codes)

Use `--theme dark` or `--theme light` for maximum compatibility.

## Implementation Details

### Language Detection

File extension mapping automatically detects the language:

```python
language_map = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    # ... and more
}
```

### Tokenization

Each language has custom tokenization logic:

1. **String extraction** - Identify and protect string literals
2. **Comment handling** - Single-line and multi-line comments
3. **Keyword matching** - Language-specific keyword sets
4. **Function/Class detection** - Regex patterns for definitions
5. **Number recognition** - Integer and float literals
6. **Builtin identification** - Standard library functions/types

### Performance

- **Fast tokenization** - Regex-based parsing
- **Lazy highlighting** - Only highlights visible lines
- **Memory efficient** - Streams large files
- **No external dependencies** - Pure Python implementation

## Future Enhancements

Potential improvements:

1. **More languages** - PHP, Ruby, Swift, Kotlin, etc.
2. **Custom themes** - User-defined color schemes
3. **Semantic highlighting** - Context-aware coloring
4. **Error highlighting** - Syntax error detection
5. **LSP integration** - Language server support
6. **Code folding** - Collapse/expand blocks
7. **Minimap** - File overview sidebar

## Troubleshooting

### No colors appearing

```bash
# Check if colors are enabled
echo -e "\033[91mRed Text\033[0m"

# Try basic dark theme
agentix view file.py --theme dark
```

### Garbled color codes

```bash
# Use basic themes only
agentix view file.py --theme dark  # or --theme light
```

### Wrong language detected

The highlighter auto-detects language from file extension. For non-standard extensions, the language may not be detected correctly.

## Contributing

To add support for a new language:

1. Add keywords to `LanguageDefinition` class
2. Implement `_highlight_<language>` method in `SyntaxHighlighter`
3. Add language mapping in `language_map`
4. Test with sample files

See `agentix/syntax_highlighter.py` for examples.

---

**Happy coding with colorful syntax! 🎨**
