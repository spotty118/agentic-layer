#!/usr/bin/env python3
"""
Test script for syntax highlighting functionality.
This demonstrates the syntax highlighting capabilities of the terminal IDE.
"""

from agentix.syntax_highlighter import SyntaxHighlighter, ColorScheme
from agentix.code_viewer import CodeViewer


def test_python_highlighting():
    """Test Python syntax highlighting."""
    print("\n" + "="*80)
    print("Testing Python Syntax Highlighting")
    print("="*80 + "\n")

    python_code = '''
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n

    # Use dynamic programming
    fib = [0, 1]
    for i in range(2, n + 1):
        fib.append(fib[i-1] + fib[i-2])

    return fib[n]

# Test the function
result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''

    highlighter = SyntaxHighlighter(ColorScheme.DARK)
    highlighted = highlighter.highlight(python_code, 'python')
    print(highlighted)


def test_javascript_highlighting():
    """Test JavaScript syntax highlighting."""
    print("\n" + "="*80)
    print("Testing JavaScript Syntax Highlighting")
    print("="*80 + "\n")

    js_code = '''
// Async function example
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

// Class example
class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }

    greet() {
        return `Hello, ${this.name}!`;
    }
}
'''

    highlighter = SyntaxHighlighter(ColorScheme.DARK)
    highlighted = highlighter.highlight(js_code, 'javascript')
    print(highlighted)


def test_code_viewer():
    """Test the code viewer with this file."""
    print("\n" + "="*80)
    print("Testing Code Viewer with Current File")
    print("="*80 + "\n")

    viewer = CodeViewer(ColorScheme.DARK)

    # View lines 1-30 of this file
    output = viewer.view_file(
        __file__,
        show_line_numbers=True,
        start_line=1,
        end_line=30
    )
    print(output)


def test_themes():
    """Test different color themes."""
    print("\n" + "="*80)
    print("Testing Different Color Themes")
    print("="*80 + "\n")

    sample_code = '''
def hello_world():
    """Print hello world."""
    message = "Hello, World!"
    print(message)
    return True
'''

    themes = [
        (ColorScheme.DARK, "Dark Theme"),
        (ColorScheme.MONOKAI, "Monokai Theme"),
        (ColorScheme.DRACULA, "Dracula Theme"),
    ]

    for theme, name in themes:
        print(f"\n{name}:")
        print("-" * 40)
        highlighter = SyntaxHighlighter(theme)
        highlighted = highlighter.highlight(sample_code, 'python')
        print(highlighted)


def main():
    """Run all tests."""
    print("\n🎨 Syntax Highlighting Test Suite")
    print("=" * 80)

    test_python_highlighting()
    test_javascript_highlighting()
    test_themes()
    test_code_viewer()

    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
