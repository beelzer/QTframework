# Quick Start Guide

## Installation

Install Qt Framework using pip:

```bash
pip install qt-framework
```

## Your First Application

Create a simple Qt application in just a few lines:

```python
from qtframework import Application, MainWindow

# Create the application
app = Application()

# Create the main window
window = MainWindow(
    title="My First Qt App",
    width=800,
    height=600
)

# Show the window
window.show()

# Run the application
app.exec()
```

## Adding Widgets

Add widgets to your application:

```python
from qtframework import Application, MainWindow
from qtframework.widgets import Button, Label

app = Application()
window = MainWindow(title="Widget Example")

# Create widgets
label = Label("Hello, Qt Framework!")
button = Button("Click Me")

# Connect button click to action
button.clicked.connect(lambda: label.setText("Button clicked!"))

# Add widgets to window
window.add_widget(label)
window.add_widget(button)

window.show()
app.exec()
```

## Using Themes

Apply beautiful themes to your application:

```python
from qtframework import Application, MainWindow
from qtframework.themes import DarkTheme

app = Application()

# Apply dark theme
app.set_theme(DarkTheme())

window = MainWindow(title="Themed App")
window.show()
app.exec()
```

## Next Steps

- Read the {doc}`api/index` for detailed API documentation
- Explore the source code examples in the repository
- Check out the comprehensive test suite for usage patterns
