from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from qtframework.config.config import Config
from qtframework.config.manager import ConfigManager
from tests.utils.test_helpers import PerformanceTimer


if TYPE_CHECKING:
    from pathlib import Path

    from pytest_qt.qtbot import QtBot


@pytest.mark.performance
class TestConfigPerformance:
    """Performance tests for configuration system."""

    def test_config_load_performance(self, tmp_path: Path) -> None:
        """Test configuration loading performance."""
        config_file = tmp_path / "large_config.yaml"

        # Create large config
        large_config = {
            f"section_{i}": {f"key_{j}": f"value_{i}_{j}" for j in range(100)} for i in range(50)
        }

        import yaml

        config_file.write_text(yaml.dump(large_config))

        with PerformanceTimer("Config Load") as timer:
            manager = ConfigManager(str(config_file))
            manager.load()

        # Should load in reasonable time
        assert timer.elapsed_ms < 1000  # Less than 1 second
        print(f"Config load time: {timer.elapsed_ms:.2f}ms")

    def test_config_access_performance(self) -> None:
        """Test configuration access performance."""
        # Create nested config
        config_data = {}
        for i in range(10):
            level1 = {}
            for j in range(10):
                level2 = {}
                for k in range(10):
                    level2[f"key_{k}"] = f"value_{i}_{j}_{k}"
                level1[f"level2_{j}"] = level2
            config_data[f"level1_{i}"] = level1

        config = Config(config_data)

        # Test nested access performance
        with PerformanceTimer("Config Access") as timer:
            for _ in range(1000):
                value = config.get("level1_5.level2_5.key_5")
                assert value == "value_5_5_5"

        # Should be very fast
        assert timer.elapsed_ms < 100  # Less than 100ms for 1000 accesses
        print(f"Config access time: {timer.elapsed_ms:.2f}ms for 1000 operations")

    def test_config_update_performance(self) -> None:
        """Test configuration update performance."""
        config = Config({})

        with PerformanceTimer("Config Updates") as timer:
            for i in range(1000):
                config.set(f"key_{i}", f"value_{i}")

        assert timer.elapsed_ms < 200  # Less than 200ms for 1000 updates
        print(f"Config update time: {timer.elapsed_ms:.2f}ms for 1000 operations")

        # Verify all values were set
        assert len(config.to_dict()) == 1000


@pytest.mark.performance
@pytest.mark.gui
class TestWidgetPerformance:
    """Performance tests for widget operations."""

    def test_widget_creation_performance(self, qtbot: QtBot) -> None:
        """Test widget creation performance."""
        parent = QWidget()
        qtbot.addWidget(parent)

        with PerformanceTimer("Widget Creation") as timer:
            buttons = []
            for i in range(100):
                button = QPushButton(f"Button {i}", parent)
                buttons.append(button)

        assert timer.elapsed_ms < 500  # Less than 500ms for 100 widgets
        print(f"Widget creation time: {timer.elapsed_ms:.2f}ms for 100 widgets")

    def test_layout_performance(self, qtbot: QtBot) -> None:
        """Test layout performance with many widgets."""
        parent = QWidget()
        qtbot.addWidget(parent)
        layout = QVBoxLayout(parent)

        # Create many widgets
        widgets = [QPushButton(f"Button {i}") for i in range(100)]

        with PerformanceTimer("Layout Addition") as timer:
            for widget in widgets:
                layout.addWidget(widget)

        assert timer.elapsed_ms < 300  # Less than 300ms
        print(f"Layout addition time: {timer.elapsed_ms:.2f}ms for 100 widgets")

    def test_widget_update_performance(self, qtbot: QtBot) -> None:
        """Test widget update performance."""
        buttons = []
        for i in range(50):
            button = QPushButton(f"Button {i}")
            qtbot.addWidget(button)
            buttons.append(button)

        with PerformanceTimer("Widget Updates") as timer:
            for _ in range(10):
                for button in buttons:
                    button.setText(f"Updated {time.time()}")
                    button.setEnabled(not button.isEnabled())

        assert timer.elapsed_ms < 500  # Less than 500ms for 500 updates
        print(f"Widget update time: {timer.elapsed_ms:.2f}ms for 500 operations")

    def test_event_processing_performance(self, qtbot: QtBot) -> None:
        """Test event processing performance."""
        widget = QWidget()
        qtbot.addWidget(widget)

        click_count = 0

        def on_timeout():
            nonlocal click_count
            click_count += 1

        timer = QTimer()
        timer.timeout.connect(on_timeout)
        timer.setInterval(1)  # 1ms interval

        with PerformanceTimer("Event Processing") as perf_timer:
            timer.start()
            qtbot.wait(100)  # Wait 100ms
            timer.stop()

        # Should process many events quickly
        assert click_count > 50  # At least 50 events in 100ms
        print(f"Processed {click_count} events in {perf_timer.elapsed_ms:.2f}ms")


@pytest.mark.performance
class TestTranslationPerformance:
    """Performance tests for translation system."""

    def test_translation_lookup_performance(self) -> None:
        """Test translation lookup performance."""
        # Create translation dictionary
        translations = {f"key_{i}": f"Translation {i}" for i in range(10000)}

        def translate(key: str) -> str:
            return translations.get(key, key)

        with PerformanceTimer("Translation Lookup") as timer:
            for i in range(1000):
                result = translate(f"key_{i}")
                assert result == f"Translation {i}"

        assert timer.elapsed_ms < 50  # Less than 50ms for 1000 lookups
        print(f"Translation lookup time: {timer.elapsed_ms:.2f}ms for 1000 operations")

    def test_translation_formatting_performance(self) -> None:
        """Test translation string formatting performance."""
        template = "Hello {name}, you have {count} new {item}!"

        with PerformanceTimer("Translation Formatting") as timer:
            for i in range(1000):
                result = template.format(
                    name=f"User{i}",
                    count=i,
                    item="messages" if i != 1 else "message",
                )
                assert "Hello User" in result

        assert timer.elapsed_ms < 100  # Less than 100ms for 1000 formats
        print(f"Translation formatting time: {timer.elapsed_ms:.2f}ms for 1000 operations")


@pytest.mark.performance
class TestMemoryUsage:
    """Tests for memory usage and leaks."""

    def test_config_memory_usage(self) -> None:
        """Test configuration memory usage."""
        import sys

        configs = []
        initial_size = 0

        for i in range(100):
            config = Config({f"key_{j}": f"value_{j}" for j in range(100)})
            configs.append(config)

            if i == 0:
                initial_size = sys.getsizeof(config.to_dict())

        # Check that memory usage is reasonable
        final_size = sum(sys.getsizeof(c.to_dict()) for c in configs)
        expected_max = initial_size * 100 * 1.5  # Allow 50% overhead

        assert final_size < expected_max
        print(f"Memory usage for 100 configs: {final_size / 1024:.2f} KB")

    def test_widget_cleanup(self, qtbot: QtBot) -> None:
        """Test that widgets are properly cleaned up."""
        import gc
        import weakref

        refs = []

        def create_widgets():
            for _i in range(10):
                widget = QWidget()
                qtbot.addWidget(widget)
                refs.append(weakref.ref(widget))
                widget.deleteLater()

        create_widgets()

        # Force garbage collection
        gc.collect()
        qtbot.wait(100)  # Let Qt process deleteLater
        gc.collect()

        # Check that widgets were cleaned up
        alive_count = sum(1 for ref in refs if ref() is not None)
        assert alive_count == 0, f"{alive_count} widgets still alive after cleanup"


# Benchmark utilities
class Benchmark:
    """Simple benchmark runner."""

    @staticmethod
    def run(func, iterations: int = 1000, name: str = "Benchmark") -> float:
        """Run a benchmark and return average time."""
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        avg_time = sum(times) / len(times) * 1000  # Convert to ms
        min_time = min(times) * 1000
        max_time = max(times) * 1000

        print(f"\n{name} Results ({iterations} iterations):")
        print(f"  Average: {avg_time:.3f}ms")
        print(f"  Min: {min_time:.3f}ms")
        print(f"  Max: {max_time:.3f}ms")

        return avg_time


@pytest.mark.performance
@pytest.mark.slow
class TestBenchmarks:
    """Comprehensive benchmarks."""

    def test_comprehensive_benchmark(self, tmp_path: Path) -> None:
        """Run comprehensive performance benchmarks."""
        results = {}

        # Config benchmark
        config = Config({"test": "value"})
        results["config_get"] = Benchmark.run(
            lambda: config.get("test"),
            iterations=10000,
            name="Config Get",
        )

        results["config_set"] = Benchmark.run(
            lambda: config.set("new_key", "new_value"),
            iterations=1000,
            name="Config Set",
        )

        # String operations benchmark
        test_string = "Hello {name}, welcome to {app}!"
        results["string_format"] = Benchmark.run(
            lambda: test_string.format(name="User", app="App"),
            iterations=10000,
            name="String Format",
        )

        # Dictionary operations benchmark
        test_dict = {f"key_{i}": f"value_{i}" for i in range(100)}
        results["dict_access"] = Benchmark.run(
            lambda: test_dict.get("key_50"),
            iterations=10000,
            name="Dict Access",
        )

        # Assert all benchmarks completed within reasonable time
        for name, time_ms in results.items():
            assert time_ms < 1.0, f"{name} took too long: {time_ms:.3f}ms"

        print("\nBenchmark Summary:")
        for name, time_ms in results.items():
            print(f"  {name}: {time_ms:.3f}ms")
