# Internationalization (i18n) Guide

Qt Framework includes comprehensive internationalization support powered by Babel, making it easy to translate your application into multiple languages.

## Overview

The i18n system provides:

- **Translation Management** - Extract, compile, and manage translations
- **Runtime Language Switching** - Change language without restarting
- **Plural Forms** - Handle plural translations correctly
- **Context Support** - Disambiguate identical strings
- **Format Support** - Numbers, dates, currencies with locale awareness
- **Lazy Translations** - Translate at render time, not definition time

## Quick Start

### Basic Translation

```python
from qtframework.i18n import gettext as _, ngettext, setup_i18n
from qtframework.core import Application
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

# Setup i18n
setup_i18n(
    domain="myapp",
    localedir="locales",
    languages=["en", "es", "fr"]
)

# Use translations
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Simple translation
        label1 = QLabel(_("Hello, World!"))

        # With context
        label2 = QLabel(_("Open", context="menu"))

        # Plural forms
        count = 5
        label3 = QLabel(ngettext(
            "You have {n} message",
            "You have {n} messages",
            count
        ).format(n=count))

        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        self.setLayout(layout)

app = Application()
window = MyWidget()
window.show()
app.exec()
```

## Setup

### Initialize i18n

```python
from qtframework.i18n import BabelManager

babel = BabelManager(
    domain="myapp",           # Translation domain
    localedir="locales",      # Where .po/.mo files live
    default_locale="en_US",   # Default language
    fallback_locale="en"      # Fallback if translation missing
)

# Set current locale
babel.set_locale("es_ES")
```

### Project Structure

```
myapp/
├── locales/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── myapp.po
│   │       └── myapp.mo
│   ├── es/
│   │   └── LC_MESSAGES/
│   │       ├── myapp.po
│   │       └── myapp.mo
│   └── fr/
│       └── LC_MESSAGES/
│           ├── myapp.po
│           └── myapp.mo
└── src/
    └── myapp/
        └── ...
```

## Translation Functions

### Basic Translation

```python
from qtframework.i18n import gettext as _

# Simple translation
message = _("Hello")

# With variables
name = "Alice"
greeting = _("Hello, {name}!").format(name=name)
```

### Context Translations

Disambiguate identical strings:

```python
from qtframework.i18n import pgettext

# "Open" as a menu action
menu_open = pgettext("menu", "Open")

# "Open" as a state
state_open = pgettext("state", "Open")
```

### Plural Forms

```python
from qtframework.i18n import ngettext

def show_items(count):
    message = ngettext(
        "You have {n} item",
        "You have {n} items",
        count
    ).format(n=count)
    print(message)

show_items(1)   # "You have 1 item"
show_items(5)   # "You have 5 items"
```

### Lazy Translations

For class-level strings that need translation at render time:

```python
from qtframework.i18n import lazy_gettext as _l

class MyWidget(QWidget):
    # Translated when accessed, not when defined
    title = _l("My Widget Title")

    def __init__(self):
        super().__init__()
        # Force evaluation
        self.setWindowTitle(str(self.title))
```

## Extracting Translations

### Mark Strings for Translation

```python
# Use _() for all user-facing strings
button_text = _("Click Me")
error_msg = _("File not found: {filename}").format(filename=path)
tooltip = _("Save the current document")

# Use context for disambiguation
save_verb = pgettext("action", "Save")
save_noun = pgettext("menu", "Save")
```

### Extract to .pot File

Use the babel extractor:

```bash
# Extract from Python files
pybabel extract -F babel.cfg -o locales/myapp.pot src/

# babel.cfg example:
# [python: **.py]
# encoding = utf-8
```

Or use Qt Framework's extractor:

```python
from qtframework.i18n import extract_messages

extract_messages(
    source_dir="src/myapp",
    output_file="locales/myapp.pot",
    keywords=["_", "gettext", "ngettext:1,2", "pgettext:1c,2c"]
)
```

### Initialize Language Files

```bash
# Create .po file for Spanish
pybabel init -i locales/myapp.pot -d locales -l es

# Create .po file for French
pybabel init -i locales/myapp.pot -d locales -l fr
```

### Update Existing Translations

```bash
# After adding new strings, update .po files
pybabel update -i locales/myapp.pot -d locales
```

### Compile Translations

```bash
# Compile .po to .mo files
pybabel compile -d locales
```

## Translation Workflow

### 1. Mark Strings

```python
from qtframework.i18n import gettext as _

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("Login"))

        self.username_label = QLabel(_("Username:"))
        self.password_label = QLabel(_("Password:"))
        self.login_button = QPushButton(_("Log In"))
        self.cancel_button = QPushButton(_("Cancel"))

        # Placeholder text
        self.username_input.setPlaceholderText(_("Enter your username"))
```

### 2. Extract Messages

```bash
pybabel extract -F babel.cfg -o locales/myapp.pot src/
```

### 3. Translate in .po Files

Edit `locales/es/LC_MESSAGES/myapp.po`:

```po
msgid "Login"
msgstr "Iniciar sesión"

msgid "Username:"
msgstr "Nombre de usuario:"

msgid "Password:"
msgstr "Contraseña:"

msgid "Log In"
msgstr "Entrar"

msgid "Cancel"
msgstr "Cancelar"

msgid "Enter your username"
msgstr "Ingrese su nombre de usuario"
```

### 4. Compile

```bash
pybabel compile -d locales
```

### 5. Switch Language

```python
babel.set_locale("es_ES")
```

## Runtime Language Switching

### Language Switcher Widget

```python
from PySide6.QtWidgets import QComboBox
from qtframework.i18n import BabelManager, gettext as _

class LanguageSwitcher(QComboBox):
    def __init__(self, babel_manager: BabelManager):
        super().__init__()
        self.babel = babel_manager

        # Add languages
        self.addItem("English", "en_US")
        self.addItem("Español", "es_ES")
        self.addItem("Français", "fr_FR")

        # Connect change event
        self.currentIndexChanged.connect(self.on_language_changed)

    def on_language_changed(self, index):
        locale = self.itemData(index)
        self.babel.set_locale(locale)

        # Emit signal to update UI
        self.language_changed.emit(locale)
```

### Updating UI After Language Change

```python
from PySide6.QtCore import Signal

class TranslatableWidget(QWidget):
    def __init__(self, babel_manager):
        super().__init__()
        self.babel = babel_manager

        # Connect to language changes
        babel_manager.locale_changed.connect(self.retranslate_ui)

        # Initial translation
        self.retranslate_ui()

    def retranslate_ui(self):
        """Update all translatable strings."""
        self.title_label.setText(_("Welcome"))
        self.subtitle_label.setText(_("Choose an option below"))
        self.ok_button.setText(_("OK"))
        self.cancel_button.setText(_("Cancel"))
```

## Formatting

### Numbers

```python
from qtframework.i18n import format_number

# Format with locale
num = 1234567.89

format_number(num, locale="en_US")  # "1,234,567.89"
format_number(num, locale="de_DE")  # "1.234.567,89"
format_number(num, locale="fr_FR")  # "1 234 567,89"
```

### Currencies

```python
from qtframework.i18n import format_currency

amount = 1234.56

format_currency(amount, "USD", locale="en_US")  # "$1,234.56"
format_currency(amount, "EUR", locale="de_DE")  # "1.234,56 €"
format_currency(amount, "JPY", locale="ja_JP")  # "¥1,235"
```

### Dates

```python
from qtframework.i18n import format_date, format_datetime, format_time
from datetime import datetime

now = datetime.now()

# Date formats
format_date(now, locale="en_US")           # "Jan 15, 2025"
format_date(now, format="full", locale="en_US")  # "Wednesday, January 15, 2025"

# Time formats
format_time(now, locale="en_US")           # "3:45:30 PM"
format_time(now, format="short", locale="en_US")  # "3:45 PM"

# Datetime formats
format_datetime(now, locale="en_US")       # "Jan 15, 2025, 3:45:30 PM"
```

### Relative Time

```python
from qtframework.i18n import format_timedelta
from datetime import timedelta

delta = timedelta(hours=2, minutes=30)
format_timedelta(delta, locale="en_US")  # "2 hours"

delta = timedelta(days=3)
format_timedelta(delta, locale="en_US")  # "3 days"
```

## Translatable Widgets

### Pre-translated Widgets

Qt Framework provides widgets with built-in i18n support:

```python
from qtframework.i18n.widgets import (
    TranslatableLabel,
    TranslatableButton,
    TranslatablePushButton
)

# Labels that auto-update on language change
label = TranslatableLabel(_("Welcome"))

# Buttons with translatable text
button = TranslatablePushButton(_("Submit"))

# When language changes, widgets automatically update
babel.set_locale("es_ES")  # Widgets now show Spanish text
```

## Context System

### Translation Contexts

Group related translations:

```python
from qtframework.i18n import TranslationContext

# Define context
class MenuContext(TranslationContext):
    context = "menu"

    file_open = _("Open")
    file_save = _("Save")
    edit_copy = _("Copy")
    edit_paste = _("Paste")

# Define another context
class DialogContext(TranslationContext):
    context = "dialog"

    ok = _("OK")
    cancel = _("Cancel")
    apply = _("Apply")
    close = _("Close")

# Use
menu_text = MenuContext.file_open  # Will use "menu" context
dialog_text = DialogContext.ok     # Will use "dialog" context
```

## Best Practices

1. **Mark Early** - Mark all user-facing strings from the start
2. **Use Context** - Add context for ambiguous strings
3. **Avoid String Concatenation** - Use format strings instead
4. **Full Sentences** - Translate complete sentences, not fragments
5. **Comments for Translators** - Add comments explaining context
6. **Test All Languages** - Switch languages to test layout
7. **Professional Translation** - Use professional translators for production
8. **Update Regularly** - Keep translations in sync with code changes

## Advanced Topics

### Custom Extractors

```python
from qtframework.i18n import MessageExtractor

class CustomExtractor(MessageExtractor):
    """Extract from custom file formats."""

    def extract(self, filename):
        messages = []
        # Custom extraction logic
        return messages

extractor = CustomExtractor()
extractor.extract_from_directory("src/")
```

### Translation Memory

```python
from qtframework.i18n import TranslationMemory

tm = TranslationMemory("memory.tmx")

# Add translation
tm.add("Hello", "Hola", source_lang="en", target_lang="es")

# Search for similar
suggestions = tm.search("Hello, World!")
```

### Validation

```python
from qtframework.i18n import validate_translations

# Check for issues
issues = validate_translations("locales/")

for issue in issues:
    print(f"{issue.file}: {issue.message}")
    # Example: "Missing plural form for 'items'"
    # Example: "Untranslated string: 'Submit'"
```

## Complete Example

```python
from qtframework.core import Application, MainWindow
from qtframework.i18n import BabelManager, gettext as _
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox

# Setup i18n
babel = BabelManager(domain="myapp", localedir="locales")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Language switcher
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("Français", "fr")
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        # Translatable content
        self.title = QLabel()
        self.message = QLabel()
        self.button = QPushButton()
        self.button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.addWidget(self.lang_combo)
        layout.addWidget(self.title)
        layout.addWidget(self.message)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Initial translation
        self.retranslate()

    def change_language(self, index):
        locale = self.lang_combo.itemData(index)
        babel.set_locale(locale)
        self.retranslate()

    def retranslate(self):
        """Update all translatable strings."""
        self.setWindowTitle(_("My Application"))
        self.title.setText(_("Welcome!"))
        self.message.setText(_("Please select your language above."))
        self.button.setText(_("Click Me"))

    def on_click(self):
        QMessageBox.information(
            self,
            _("Information"),
            _("Button was clicked!")
        )

app = Application()
window = MainWindow()
window.show()
app.exec()
```
