"""Tests for configuration providers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import yaml

from qtframework.config.providers import EnvProvider, FileProvider, JsonProvider, YamlProvider


class TestFileProvider:
    """Test FileProvider base class."""

    def test_file_provider_creation(self) -> None:
        """Test creating file provider."""
        provider = FileProvider("/path/to/config.json")
        assert provider.path == "/path/to/config.json"

    def test_file_provider_load_returns_empty(self) -> None:
        """Test base file provider load returns empty dict."""
        provider = FileProvider("/path/to/config.json")
        result = provider.load()
        assert result == {}

    def test_file_provider_save_returns_true(self) -> None:
        """Test base file provider save returns True."""
        provider = FileProvider("/path/to/config.json")
        result = provider.save({"key": "value"})
        assert result is True


class TestJsonProvider:
    """Test JsonProvider."""

    def test_json_provider_creation(self) -> None:
        """Test creating JSON provider."""
        provider = JsonProvider("/path/to/config.json")
        assert provider.path == "/path/to/config.json"

    def test_json_provider_load_valid_file(self) -> None:
        """Test loading valid JSON file."""
        data = {"app": {"name": "test"}, "debug": True}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            f.flush()
            path = f.name

        try:
            provider = JsonProvider(path)
            result = provider.load()
            assert result == data
        finally:
            Path(path).unlink()

    def test_json_provider_load_nonexistent_file(self) -> None:
        """Test loading nonexistent JSON file returns empty dict."""
        provider = JsonProvider("/nonexistent/file.json")
        result = provider.load()
        assert result == {}

    def test_json_provider_load_invalid_json(self) -> None:
        """Test loading invalid JSON returns empty dict."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            f.write("{invalid json")
            f.flush()
            path = f.name

        try:
            provider = JsonProvider(path)
            result = provider.load()
            assert result == {}
        finally:
            Path(path).unlink()

    def test_json_provider_load_empty_file(self) -> None:
        """Test loading empty JSON file."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            f.write("")
            f.flush()
            path = f.name

        try:
            provider = JsonProvider(path)
            result = provider.load()
            assert result == {}
        finally:
            Path(path).unlink()

    def test_json_provider_load_nested_data(self) -> None:
        """Test loading nested JSON data."""
        data = {
            "app": {"name": "test", "version": "1.0"},
            "database": {"host": "localhost", "port": 5432},
        }

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            f.flush()
            path = f.name

        try:
            provider = JsonProvider(path)
            result = provider.load()
            assert result["app"]["name"] == "test"
            assert result["database"]["port"] == 5432
        finally:
            Path(path).unlink()


class TestYamlProvider:
    """Test YamlProvider."""

    def test_yaml_provider_creation(self) -> None:
        """Test creating YAML provider."""
        provider = YamlProvider("/path/to/config.yaml")
        assert provider.path == "/path/to/config.yaml"

    def test_yaml_provider_load_valid_file(self) -> None:
        """Test loading valid YAML file."""
        data = {"app": {"name": "test"}, "debug": True}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            yaml.safe_dump(data, f)
            f.flush()
            path = f.name

        try:
            provider = YamlProvider(path)
            result = provider.load()
            assert result == data
        finally:
            Path(path).unlink()

    def test_yaml_provider_load_nonexistent_file(self) -> None:
        """Test loading nonexistent YAML file returns empty dict."""
        provider = YamlProvider("/nonexistent/file.yaml")
        result = provider.load()
        assert result == {}

    def test_yaml_provider_load_invalid_yaml(self) -> None:
        """Test loading invalid YAML returns empty dict."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            f.write("invalid: yaml: syntax: error")
            f.flush()
            path = f.name

        try:
            provider = YamlProvider(path)
            result = provider.load()
            assert result == {}
        finally:
            Path(path).unlink()

    def test_yaml_provider_load_empty_file(self) -> None:
        """Test loading empty YAML file returns empty dict."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            f.write("")
            f.flush()
            path = f.name

        try:
            provider = YamlProvider(path)
            result = provider.load()
            assert result == {}
        finally:
            Path(path).unlink()

    def test_yaml_provider_load_null_content(self) -> None:
        """Test loading YAML with null content."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            f.write("null")
            f.flush()
            path = f.name

        try:
            provider = YamlProvider(path)
            result = provider.load()
            assert result == {}
        finally:
            Path(path).unlink()

    def test_yaml_provider_load_nested_data(self) -> None:
        """Test loading nested YAML data."""
        data = {
            "app": {"name": "test", "version": "1.0"},
            "database": {"host": "localhost", "port": 5432},
        }

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            yaml.safe_dump(data, f)
            f.flush()
            path = f.name

        try:
            provider = YamlProvider(path)
            result = provider.load()
            assert result["app"]["name"] == "test"
            assert result["database"]["port"] == 5432
        finally:
            Path(path).unlink()


class TestEnvProvider:
    """Test EnvProvider."""

    def test_env_provider_creation_no_prefix(self) -> None:
        """Test creating env provider without prefix."""
        provider = EnvProvider()
        assert provider.prefix == ""

    def test_env_provider_creation_with_prefix(self) -> None:
        """Test creating env provider with prefix."""
        provider = EnvProvider(prefix="APP_")
        assert provider.prefix == "APP_"

    def test_env_provider_load_no_prefix(self) -> None:
        """Test loading from environment without prefix."""
        # Set test environment variable
        os.environ["TEST_VAR"] = "test_value"

        try:
            provider = EnvProvider()
            result = provider.load()

            assert "TEST_VAR" in result
            assert result["TEST_VAR"] == "test_value"
        finally:
            del os.environ["TEST_VAR"]

    def test_env_provider_load_with_prefix(self) -> None:
        """Test loading from environment with prefix."""
        os.environ["APP_NAME"] = "TestApp"
        os.environ["APP_VERSION"] = "1.0"
        os.environ["OTHER_VAR"] = "ignored"

        try:
            provider = EnvProvider(prefix="APP_")
            result = provider.load()

            assert "APP_NAME" in result
            assert "APP_VERSION" in result
            assert "OTHER_VAR" not in result
            assert result["APP_NAME"] == "TestApp"
            assert result["APP_VERSION"] == "1.0"
        finally:
            del os.environ["APP_NAME"]
            del os.environ["APP_VERSION"]
            del os.environ["OTHER_VAR"]

    def test_env_provider_load_empty_prefix(self) -> None:
        """Test loading with empty prefix loads all variables."""
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "value2"

        try:
            provider = EnvProvider(prefix="")
            result = provider.load()

            assert "VAR1" in result
            assert "VAR2" in result
        finally:
            del os.environ["VAR1"]
            del os.environ["VAR2"]

    def test_env_provider_save_returns_false(self) -> None:
        """Test env provider save returns False."""
        provider = EnvProvider()
        result = provider.save({"key": "value"})
        assert result is False

    def test_env_provider_prefix_filtering(self) -> None:
        """Test env provider filters by prefix."""
        os.environ["MYAPP_VAR1"] = "value1"
        os.environ["MYAPP_VAR2"] = "value2"
        os.environ["OTHER_VAR"] = "other"

        try:
            provider = EnvProvider(prefix="MYAPP_")
            result = provider.load()

            assert "MYAPP_VAR1" in result
            assert "MYAPP_VAR2" in result
            assert "OTHER_VAR" not in result
        finally:
            del os.environ["MYAPP_VAR1"]
            del os.environ["MYAPP_VAR2"]
            del os.environ["OTHER_VAR"]

    def test_env_provider_no_matching_vars(self) -> None:
        """Test env provider with no matching variables."""
        provider = EnvProvider(prefix="NONEXISTENT_")
        result = provider.load()

        # Should return dict with no NONEXISTENT_ prefixed vars
        for key in result:
            assert not key.startswith("NONEXISTENT_")


class TestProviderInheritance:
    """Test provider inheritance."""

    def test_json_provider_inherits_file_provider(self) -> None:
        """Test JsonProvider inherits from FileProvider."""
        provider = JsonProvider("/path/to/file.json")
        assert isinstance(provider, FileProvider)

    def test_yaml_provider_inherits_file_provider(self) -> None:
        """Test YamlProvider inherits from FileProvider."""
        provider = YamlProvider("/path/to/file.yaml")
        assert isinstance(provider, FileProvider)

    def test_file_provider_has_path_attribute(self) -> None:
        """Test FileProvider has path attribute."""
        provider = FileProvider("/test/path")
        assert hasattr(provider, "path")
        assert provider.path == "/test/path"

    def test_env_provider_has_prefix_attribute(self) -> None:
        """Test EnvProvider has prefix attribute."""
        provider = EnvProvider(prefix="TEST_")
        assert hasattr(provider, "prefix")
        assert provider.prefix == "TEST_"
