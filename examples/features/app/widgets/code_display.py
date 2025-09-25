"""
Code display widget with syntax highlighting.
"""

from __future__ import annotations

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QPalette, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QApplication, QTextEdit


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""

    def __init__(self, parent=None, dark_theme=False):
        super().__init__(parent)
        self.dark_theme = dark_theme
        self.highlighting_rules = []
        self._setup_rules()

    def _is_dark_theme(self):
        """Determine if we're using a dark theme."""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check if background is dark
            bg_color = palette.color(QPalette.Window)
            return bg_color.lightness() < 128
        return False

    def _get_theme_syntax_colors(self):
        """Get syntax colors from the current theme."""
        # Try to get colors from the theme manager
        try:
            # Import here to avoid circular imports

            # Try to access the theme manager from the main window
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

    def _setup_rules(self):
        """Set up highlighting rules with theme-aware colors."""
        # Get colors from theme or defaults
        colors = self._get_theme_syntax_colors()

        keyword_color = colors["keyword"]
        class_color = colors["class"]
        function_color = colors["function"]
        string_color = colors["string"]
        comment_color = colors["comment"]
        number_color = colors["number"]

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(keyword_color))
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
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Class names (Qt classes and general)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(class_color))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression("\\bQ[A-Za-z]+\\b"), class_format))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Z][A-Za-z0-9_]+\\b"),
            class_format,
        ))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(function_color))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"),
            function_format,
        ))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(string_color))
        # Single quotes
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format,
        ))
        # Double quotes
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format,
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(comment_color))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(number_color))
        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            number_format,
        ))

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.highlighting_rules:
            expression = pattern
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

    def rehighlight_with_theme(self):
        """Re-setup rules and rehighlight when theme changes."""
        self.highlighting_rules.clear()
        self._setup_rules()
        self.rehighlight()


class CodeDisplay(QTextEdit):
    """Widget for displaying code with syntax highlighting."""

    def __init__(self, code: str = "", language: str = "python", parent=None):
        super().__init__(parent)
        self.language = language

        # Set up the widget
        self.setReadOnly(True)

        # Apply theme-aware styling first
        self._apply_theme_styling()

        # Then set the code which will trigger height adjustment
        self.setPlainText(code)

        # Set up syntax highlighter
        if language.lower() == "python":
            self.highlighter = PythonHighlighter(self.document())

        # Connect to document changes to auto-adjust height
        self.document().contentsChanged.connect(self._adjust_height_to_content)

        # Initial height adjustment
        self._adjust_height_to_content()

    def _get_theme_font(self):
        """Get the code font and size from the current theme."""
        font_name = "Consolas"
        font_size = 12  # Default to font_size_sm

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

    def _apply_theme_styling(self):
        """Apply theme-aware styling to the code display."""
        from PySide6.QtCore import Qt

        # Get font from theme if available
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)

        # Set properties for theme styling
        self.setProperty("codeblock", "true")

        # Disable text wrapping for code - this will enable horizontal scrollbar when needed
        self.setLineWrapMode(QTextEdit.NoWrap)

        # Enable horizontal scrollbar when needed, NEVER show vertical scrollbar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set minimum height but no maximum - will grow to fit content
        self.setMinimumHeight(40)  # At least 2 lines
        self.setMinimumWidth(250)  # Ensure minimum width for code visibility

    def _adjust_height_to_content(self):
        """Adjust the height of the widget to fit ALL content without vertical scrolling."""
        # Get the document and calculate required size
        doc = self.document()

        # Get the number of lines
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
                padding += scrollbar_height + 4  # Add small buffer

        # Calculate total height - no maximum constraint since we want to show all content
        total_height = text_height + padding + 8  # Add small buffer for comfort

        # Only constrain to minimum height
        total_height = max(self.minimumHeight(), total_height)

        # Set the fixed height to fit all content
        self.setFixedHeight(int(total_height))

    def set_code(self, code: str):
        """Set the code content."""
        self.setPlainText(code)
        # Trigger height adjustment after setting new code
        self._adjust_height_to_content()

    def set_language(self, language: str):
        """Change the syntax highlighting language."""
        self.language = language
        # Could switch highlighters here if we support multiple languages

    def update_theme(self):
        """Update the highlighter and font when theme changes."""
        # Update syntax colors
        if hasattr(self, "highlighter"):
            self.highlighter.rehighlight_with_theme()

        # Update font from theme
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)

        # Readjust height after font change
        self._adjust_height_to_content()

    def resizeEvent(self, event):
        """Handle resize events to check if scrollbar visibility changes."""
        super().resizeEvent(event)
        # Readjust height when width changes (might affect horizontal scrollbar)
        self._adjust_height_to_content()
