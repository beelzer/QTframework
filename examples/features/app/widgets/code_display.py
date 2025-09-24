"""
Code display widget with syntax highlighting.
"""

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import (QColor, QFont, QPalette, QSyntaxHighlighter,
                           QTextCharFormat)
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
            import sys
            from pathlib import Path

            # Try to access the theme manager from the main window
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, 'theme_manager'):
                        current_theme = widget.theme_manager.get_current_theme()
                        if current_theme and hasattr(current_theme, 'tokens') and hasattr(current_theme.tokens, 'syntax'):
                            syntax = current_theme.tokens.syntax
                            return {
                                'keyword': syntax.keyword,
                                'class': syntax.class_name,
                                'function': syntax.function,
                                'string': syntax.string,
                                'comment': syntax.comment,
                                'number': syntax.number,
                                'operator': syntax.operator,
                                'decorator': syntax.decorator,
                            }
        except:
            pass

        # Fallback to default colors based on theme detection
        if self._is_dark_theme():
            return {
                'keyword': "#569CD6",
                'class': "#4EC9B0",
                'function': "#DCDCAA",
                'string': "#CE9178",
                'comment': "#6A9955",
                'number': "#B5CEA8",
                'operator': "#D4D4D4",
                'decorator': "#DCDCAA",
            }
        else:
            return {
                'keyword': "#0000FF",
                'class': "#267F99",
                'function': "#795E26",
                'string': "#A31515",
                'comment': "#008000",
                'number': "#098658",
                'operator': "#000000",
                'decorator': "#AA0000",
            }

    def _setup_rules(self):
        """Set up highlighting rules with theme-aware colors."""
        # Get colors from theme or defaults
        colors = self._get_theme_syntax_colors()

        keyword_color = colors['keyword']
        class_color = colors['class']
        function_color = colors['function']
        string_color = colors['string']
        comment_color = colors['comment']
        number_color = colors['number']

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(keyword_color))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda",
            "None", "nonlocal", "not", "or", "pass", "raise", "return",
            "True", "try", "while", "with", "yield", "self"
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Class names (Qt classes and general)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(class_color))
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((
            QRegularExpression("\\bQ[A-Za-z]+\\b"),
            class_format
        ))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Z][A-Za-z0-9_]+\\b"),
            class_format
        ))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(function_color))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"),
            function_format
        ))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(string_color))
        # Single quotes
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format
        ))
        # Double quotes
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(comment_color))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression("#[^\n]*"),
            comment_format
        ))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(number_color))
        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"),
            number_format
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
        self.setPlainText(code)

        # Apply theme-aware styling
        self._apply_theme_styling()

        # Set up syntax highlighter
        if language.lower() == "python":
            self.highlighter = PythonHighlighter(self.document())

    def _get_theme_font(self):
        """Get the code font and size from the current theme."""
        font_name = "Consolas"
        font_size = 12  # Default to font_size_sm

        try:
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, 'theme_manager'):
                        current_theme = widget.theme_manager.get_current_theme()
                        if current_theme and hasattr(current_theme, 'tokens'):
                            if hasattr(current_theme.tokens, 'typography'):
                                typography = current_theme.tokens.typography
                                if hasattr(typography, 'font_family_code'):
                                    font_name = typography.font_family_code
                                if hasattr(typography, 'font_size_sm'):
                                    font_size = typography.font_size_sm
                            break
        except:
            pass

        return font_name, font_size

    def _apply_theme_styling(self):
        """Apply theme-aware styling to the code display."""
        # Get font from theme if available
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)

        # Set properties for theme styling
        self.setProperty("codeblock", "true")

        # Disable text wrapping for code
        self.setLineWrapMode(QTextEdit.NoWrap)

        # Set reasonable size
        self.setMaximumHeight(100)
        self.setMinimumHeight(60)

    def set_code(self, code: str):
        """Set the code content."""
        self.setPlainText(code)

    def set_language(self, language: str):
        """Change the syntax highlighting language."""
        self.language = language
        # Could switch highlighters here if we support multiple languages

    def update_theme(self):
        """Update the highlighter and font when theme changes."""
        # Update syntax colors
        if hasattr(self, 'highlighter'):
            self.highlighter.rehighlight_with_theme()

        # Update font from theme
        font_name, font_size = self._get_theme_font()
        font = QFont(font_name)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(font_size)
        self.setFont(font)
