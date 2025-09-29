# QTFramework Test Suite

Comprehensive testing framework for QTFramework following 2025 best practices.

## 📁 Structure

```
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_config.py    # Configuration system tests
│   ├── test_core.py      # Core application/window tests
│   └── test_i18n.py      # Internationalization tests
├── integration/          # Integration tests for component interactions
│   └── test_app_integration.py
├── performance/          # Performance and benchmark tests
│   └── test_performance.py
├── fixtures/             # Test fixtures and factories
│   └── factories.py      # Widget, config, and data factories
├── utils/                # Test utilities and helpers
│   └── helpers.py        # Common test helpers
└── conftest.py          # Pytest configuration and global fixtures
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/qtframework --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"       # Skip slow tests
pytest -m performance      # Performance tests only
```

### Test Categories

Tests are marked with the following categories:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring multiple components
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.gui` - Tests requiring Qt GUI
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.database` - Tests requiring database

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/unit/test_config.py

# Run a specific test class
pytest tests/unit/test_config.py::TestConfig

# Run a specific test method
pytest tests/unit/test_config.py::TestConfig::test_config_initialization

# Run tests matching a pattern
pytest -k "config"

# Run with verbose output
pytest -vv
```

## 🛠️ Test Fixtures

### Global Fixtures (conftest.py)

- `qapp` - Session-scoped QApplication instance
- `qtbot` - Enhanced QtBot for GUI testing
- `main_window` - Test QMainWindow instance
- `test_widget` - Generic QWidget for testing
- `mock_settings` - Mocked QSettings
- `temp_config_file` - Temporary configuration file
- `temp_translations_dir` - Temporary translations directory
- `sample_data` - Common test data
- `mock_database` - Temporary SQLite database

### Factory Classes (fixtures/factories.py)

- `WidgetFactory` - Create test widgets
- `ConfigFactory` - Create test configurations
- `DataFactory` - Create test data
- `MockFactory` - Create mock objects
- `TestContext` - Container for test context

## 📊 Coverage

### Running Coverage

```bash
# Generate terminal report
pytest --cov=src/qtframework --cov-report=term-missing

# Generate HTML report
pytest --cov=src/qtframework --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML report (for CI)
pytest --cov=src/qtframework --cov-report=xml
```

### Coverage Goals

- Minimum overall coverage: 80%
- Unit test coverage: 90%+
- Integration test coverage: 70%+
- Critical path coverage: 100%

## 🔧 Configuration

### pytest.ini

Main pytest configuration with:

- Test discovery patterns
- Default command-line options
- Coverage settings
- Marker definitions
- Warning filters
- Qt-specific settings

### pyproject.toml

Additional configuration for:

- Coverage exclusions
- Test paths
- Tool-specific settings

## 🏃 CI/CD Integration

### GitHub Actions

The test suite runs automatically on:

- Push to main/master/develop branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual workflow dispatch

Workflow includes:

- Linting (Ruff)
- Type checking (MyPy)
- Unit tests (all platforms)
- Integration tests
- Performance tests
- Security scanning
- Coverage reporting

### Local Pre-commit

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🎯 Best Practices

### Writing Tests

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mock External Dependencies**: Use mocks for external services
5. **Test Edge Cases**: Include boundary and error conditions
6. **Performance Awareness**: Mark slow tests appropriately

### Test Organization

1. **One Test File Per Module**: Mirror source structure
2. **Logical Grouping**: Use test classes for related tests
3. **Shared Setup**: Use fixtures for common setup
4. **Descriptive Markers**: Use markers for test categorization

### GUI Testing

1. **Use QtBot**: Leverage pytest-qt's QtBot fixture
2. **Wait for Signals**: Use waitSignal for async operations
3. **Process Events**: Allow Qt event loop to process
4. **Clean Up Widgets**: Ensure proper widget cleanup

## 📈 Performance Testing

### Running Benchmarks

```bash
# Run performance tests
pytest tests/performance -m performance

# Run with benchmark plugin
pytest tests/performance --benchmark-only
```

### Performance Metrics

- Config operations: < 1ms per operation
- Widget creation: < 5ms per widget
- Translation lookup: < 0.1ms per lookup
- Memory usage: Linear growth with data size

## 🐛 Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -s

# Show detailed assertions
pytest -vv

# Show local variables on failure
pytest -l
```

### Interactive Debugging

```python
# Add breakpoint in test
import pdb; pdb.set_trace()

# Or use pytest's built-in
pytest --pdb  # Drop to debugger on failure
pytest --trace  # Drop to debugger at start
```

### Qt-specific Debugging

```bash
# Set Qt debug environment variables
export QT_DEBUG_PLUGINS=1
export QT_LOGGING_RULES="*.debug=true"
```

## 📝 Contributing

### Adding New Tests

1. Create test file in appropriate directory
2. Follow existing naming conventions
3. Add appropriate markers
4. Include docstrings for complex tests
5. Update this README if needed

### Test Review Checklist

- [ ] Tests pass locally
- [ ] Coverage maintained/improved
- [ ] Appropriate markers used
- [ ] No hardcoded paths
- [ ] Proper cleanup
- [ ] Documentation updated

## 🔗 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Qt Test Documentation](https://doc.qt.io/qt-6/qtest.html)
