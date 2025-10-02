"""Code display widget with syntax highlighting.

This module provides widgets for displaying code with syntax highlighting
and automatic height adjustment.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QColor, QFont, QPalette, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget


class CodeHighlighter(QSyntaxHighlighter):
    """Base class for language-specific syntax highlighters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self._setup_rules()

    def _is_dark_theme(self) -> bool:
        """Determine if we're using a dark theme."""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            bg_color = palette.color(QPalette.Window)
            return bg_color.lightness() < 128
        return False

    def _get_theme_syntax_colors(self) -> dict[str, str]:
        """Get syntax colors from the current theme or defaults."""
        # Try to get colors from the theme manager
        try:
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, "theme_manager"):
                        current_theme = widget.theme_manager.get_current_theme()
                        if (
                            current_theme
                            and hasattr(current_theme, "tokens")
                            and hasattr(current_theme.tokens, "syntax")
                        ):
                            syntax = current_theme.tokens.syntax
                            return {
                                "keyword": syntax.keyword,
                                "class": syntax.class_name,
                                "function": syntax.function,
                                "string": syntax.string,
                                "comment": syntax.comment,
                                "number": syntax.number,
                                "operator": syntax.operator,
                                "decorator": syntax.decorator,
                            }
        except:
            pass

        # Fallback to default colors based on theme detection
        return self._get_default_colors()

    def _get_default_colors(self) -> dict[str, str]:
        """Get default syntax colors based on theme."""
        if self._is_dark_theme():
            return {
                "keyword": "#569CD6",
                "class": "#4EC9B0",
                "function": "#DCDCAA",
                "string": "#CE9178",
                "comment": "#6A9955",
                "number": "#B5CEA8",
                "operator": "#D4D4D4",
                "decorator": "#DCDCAA",
            }
        return {
            "keyword": "#0000FF",
            "class": "#267F99",
            "function": "#795E26",
            "string": "#A31515",
            "comment": "#008000",
            "number": "#098658",
            "operator": "#000000",
            "decorator": "#AA0000",
        }

    def _setup_rules(self) -> None:
        """Set up highlighting rules - to be implemented by subclasses."""

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.highlighting_rules:
            expression = pattern
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

    def rehighlight_with_theme(self) -> None:
        """Re-setup rules and rehighlight when theme changes."""
        self.highlighting_rules.clear()
        self._setup_rules()
        self.rehighlight()


class PythonHighlighter(CodeHighlighter):
    """Syntax highlighter for Python code."""

    def _setup_rules(self) -> None:
        """Set up Python-specific highlighting rules."""
        colors = self._get_theme_syntax_colors()

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(colors["keyword"]))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and",
            "as",
            "assert",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "False",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "None",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "True",
            "try",
            "while",
            "with",
            "yield",
            "self",
            "async",
            "await",
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Class names
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(colors["class"]))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression("\\bQ[A-Za-z]+\\b"), class_format))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Z][A-Za-z0-9_]+\\b"),
            class_format,
        ))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(colors["function"]))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"),
            function_format,
        ))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors["string"]))
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format,
        ))
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format,
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors["comment"]))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors["number"]))
        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            number_format,
        ))


class JavaScriptHighlighter(CodeHighlighter):
    """Syntax highlighter for JavaScript code."""

    def _setup_rules(self) -> None:
        """Set up JavaScript-specific highlighting rules."""
        colors = self._get_theme_syntax_colors()

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(colors["keyword"]))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "async",
            "await",
            "break",
            "case",
            "catch",
            "class",
            "const",
            "continue",
            "debugger",
            "default",
            "delete",
            "do",
            "else",
            "export",
            "extends",
            "finally",
            "for",
            "function",
            "if",
            "import",
            "in",
            "instanceof",
            "let",
            "new",
            "return",
            "super",
            "switch",
            "this",
            "throw",
            "try",
            "typeof",
            "var",
            "void",
            "while",
            "with",
            "yield",
            "true",
            "false",
            "null",
            "undefined",
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(colors["function"]))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"),
            function_format,
        ))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors["string"]))
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format,
        ))
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format,
        ))
        self.highlighting_rules.append((
            QRegularExpression("`[^`\\\\]*(\\\\.[^`\\\\]*)*`"),
            string_format,
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors["comment"]))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        self.highlighting_rules.append((QRegularExpression("/\\*.*\\*/"), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors["number"]))
        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            number_format,
        ))


class CodeDisplay(QTextEdit):
    """Widget for displaying code with syntax highlighting.

    Automatically adjusts height to fit content without vertical scrolling,
    and provides horizontal scrolling for long lines.

    Example:
        ```python
        code_display = CodeDisplay(
            code='def hello():\\n    print("Hello")', language="python"
        )
        ```
    """

    def __init__(
        self,
        code: str = "",
        language: str = "python",
        parent: QWidget | None = None,
        line_numbers: bool = False,
        wrap_mode: bool = False,
    ):
        """Initialize the code display widget.

        Args:
            code: The code to display
            language: Programming language for syntax highlighting (python, javascript)
            parent: Parent widget
            line_numbers: Whether to show line numbers (future enhancement)
            wrap_mode: Whether to wrap long lines (default: False)
        """
        super().__init__(parent)
        self.language = language.lower()
        self._wrap_mode = wrap_mode

        # Set up the widget
        self.setReadOnly(True)

        # Apply theme-aware styling
        self._apply_theme_styling()

        # Set the code
        self.setPlainText(code)

        # Set up syntax highlighter based on language
        self.highlighter = self._create_highlighter()

        # Connect to document changes to auto-adjust height
        self.document().contentsChanged.connect(self._adjust_height_to_content)

        # Initial height adjustment
        self._adjust_height_to_content()

    def _create_highlighter(self) -> CodeHighlighter | None:
        """Create the appropriate syntax highlighter for the language."""
        if self.language == "python":
            return PythonHighlighter(self.document())
        if self.language in ("javascript", "js"):
            return JavaScriptHighlighter(self.document())
        return None

    def _get_theme_font(self) -> tuple[str, int]:
        """Get the code font and size from the current theme."""
        font_name = "Consolas"
        font_size = 12

        try:
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, "theme_manager"):
                        current_theme = widget.theme_manager.get_current_theme()
                        if current_theme and hasattr(current_theme, "tokens"):
                            if hasattr(current_theme.tokens, "typography"):
                                typography = current_theme.tokens.typography
                                if hasattr(typography, "font_family_code"):
                                    font_name = typography.font_family_code
                                if hasattr(typography, "font_size_sm"):
                                    font_size = typography.font_size_sm
                            break
        except:
            pass

        return font_name, font_size

    def _apply_theme_styling(self) -> None:
        """Apply theme-aware styling to the code display."""
        # Get font from theme if available
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)

        # Set properties for theme styling
        self.setProperty("codeblock", "true")

        # Set wrap mode
        if self._wrap_mode:
            self.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.setLineWrapMode(QTextEdit.NoWrap)

        # Scrollbar policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set minimum dimensions
        self.setMinimumHeight(40)
        self.setMinimumWidth(250)

    def _adjust_height_to_content(self) -> None:
        """Adjust the height of the widget to fit ALL content without vertical scrolling."""
        doc = self.document()
        line_count = doc.blockCount()

        # Get font metrics for line height
        font_metrics = self.fontMetrics()
        line_height = font_metrics.lineSpacing()

        # Calculate base height needed for text
        text_height = line_count * line_height

        # Add padding for frame, margins, and scrollbars
        margins = self.contentsMargins()
        frame_width = self.frameWidth() * 2
        padding = margins.top() + margins.bottom() + frame_width

        # Check if horizontal scrollbar will be needed
        doc_width = doc.idealWidth()
        viewport_width = self.viewport().width()
        needs_h_scrollbar = doc_width > viewport_width

        # Add height for horizontal scrollbar if needed
        if needs_h_scrollbar:
            h_scrollbar = self.horizontalScrollBar()
            if h_scrollbar:
                scrollbar_height = h_scrollbar.sizeHint().height()
                padding += scrollbar_height + 4

        # Calculate total height
        total_height = text_height + padding + 8

        # Only constrain to minimum height
        total_height = max(self.minimumHeight(), total_height)

        # Set the fixed height to fit all content
        self.setFixedHeight(int(total_height))

    def set_code(self, code: str) -> None:
        """Set the code content.

        Args:
            code: The code to display
        """
        self.setPlainText(code)
        self._adjust_height_to_content()

    def set_language(self, language: str) -> None:
        """Change the syntax highlighting language.

        Args:
            language: Programming language (python, javascript)
        """
        self.language = language.lower()
        # Remove old highlighter
        if self.highlighter:
            self.highlighter.setDocument(None)
        # Create new highlighter
        self.highlighter = self._create_highlighter()

    def copy_to_clipboard(self) -> None:
        """Copy code to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.toPlainText())

    def update_theme(self) -> None:
        """Update the highlighter and font when theme changes."""
        # Update syntax colors
        if self.highlighter:
            self.highlighter.rehighlight_with_theme()

        # Update font from theme
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)

        # Readjust height after font change
        self._adjust_height_to_content()

    def resizeEvent(self, event) -> None:
        """Handle resize events to check if scrollbar visibility changes."""
        super().resizeEvent(event)
        self._adjust_height_to_content()
