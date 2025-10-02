"""Tests for ConfigFileLoader."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from qtframework.config.file_loader import ConfigFileLoader
from qtframework.utils.exceptions import ConfigurationError


class TestConfigFileLoaderSecurity:
    """Test file security validation."""

    def test_validate_file_security_valid_file(self) -> None:
        """Test security validation passes for valid file."""
        loader = ConfigFileLoader()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write('{"key": "value"}')
            f.flush()
            path = Path(f.name)

        try:
            assert loader.validate_file_security(path) is True
        finally:
            path.unlink()

    def test_validate_file_security_too_large(self) -> None:
        """Test security validation fails for large file."""
        loader = ConfigFileLoader()
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Write file larger than MAX_FILE_SIZE
            f.write(b"x" * (ConfigFileLoader.MAX_FILE_SIZE + 1))
            f.flush()
            path = Path(f.name)

        try:
            assert loader.validate_file_security(path) is False
        finally:
            path.unlink()

    def test_validate_file_security_not_a_file(self) -> None:
        """Test security validation fails for directory."""
        loader = ConfigFileLoader()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            assert loader.validate_file_security(path) is False

    def test_validate_file_security_nonexistent(self) -> None:
        """Test security validation fails for nonexistent file."""
        loader = ConfigFileLoader()
        path = Path("/nonexistent/path/file.json")
        assert loader.validate_file_security(path) is False


class TestConfigFileLoaderJSON:
    """Test JSON file loading."""

    def test_load_json_valid(self) -> None:
        """Test loading valid JSON file."""
        loader = ConfigFileLoader()
        data = {"key": "value", "nested": {"key2": "value2"}}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(data, f)
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "json")
            assert result == data
        finally:
            path.unlink()

    def test_load_json_invalid_syntax(self) -> None:
        """Test loading JSON with invalid syntax."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("{invalid json")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                loader.load(path, "json")
            assert "Invalid JSON format" in str(exc_info.value)
        finally:
            path.unlink()

    def test_load_json_not_dict(self) -> None:
        """Test loading JSON that's not a dictionary."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(["list", "not", "dict"], f)
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                loader.load(path, "json")
            assert "must contain a dictionary" in str(exc_info.value)
        finally:
            path.unlink()

    def test_save_json(self) -> None:
        """Test saving JSON file."""
        loader = ConfigFileLoader()
        data = {"key": "value", "nested": {"key2": "value2"}}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            path = Path(f.name)

        try:
            result = loader.save(path, data, "json")
            assert result is True
            assert path.exists()

            # Verify content
            with path.open() as f:
                loaded = json.load(f)
            assert loaded == data
        finally:
            path.unlink()


class TestConfigFileLoaderYAML:
    """Test YAML file loading."""

    def test_load_yaml_valid(self) -> None:
        """Test loading valid YAML file."""
        loader = ConfigFileLoader()
        data = {"key": "value", "nested": {"key2": "value2"}}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            yaml.safe_dump(data, f)
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "yaml")
            assert result == data
        finally:
            path.unlink()

    def test_load_yml_extension(self) -> None:
        """Test loading .yml extension."""
        loader = ConfigFileLoader()
        data = {"key": "value"}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yml") as f:
            yaml.safe_dump(data, f)
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "yml")
            assert result == data
        finally:
            path.unlink()

    def test_load_yaml_invalid_syntax(self) -> None:
        """Test loading YAML with invalid syntax."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write("invalid: yaml: syntax: error")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                loader.load(path, "yaml")
            assert "Invalid YAML format" in str(exc_info.value)
        finally:
            path.unlink()

    def test_load_yaml_not_dict(self) -> None:
        """Test loading YAML that's not a dictionary."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            yaml.safe_dump(["list", "not", "dict"], f)
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                loader.load(path, "yaml")
            assert "must contain a dictionary" in str(exc_info.value)
        finally:
            path.unlink()

    def test_save_yaml(self) -> None:
        """Test saving YAML file."""
        loader = ConfigFileLoader()
        data = {"key": "value", "nested": {"key2": "value2"}}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            path = Path(f.name)

        try:
            result = loader.save(path, data, "yaml")
            assert result is True
            assert path.exists()

            # Verify content
            with path.open() as f:
                loaded = yaml.safe_load(f)
            assert loaded == data
        finally:
            path.unlink()


class TestConfigFileLoaderINI:
    """Test INI file loading."""

    def test_load_ini_valid(self) -> None:
        """Test loading valid INI file."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as f:
            f.write("[section1]\n")
            f.write("key1 = value1\n")
            f.write("[section2]\n")
            f.write("key2 = value2\n")
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "ini")
            assert "section1" in result
            assert result["section1"]["key1"] == "value1"
            assert "section2" in result
            assert result["section2"]["key2"] == "value2"
        finally:
            path.unlink()

    def test_load_ini_empty_file(self) -> None:
        """Test loading empty INI file."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "ini")
            assert result == {}
        finally:
            path.unlink()


class TestConfigFileLoaderENV:
    """Test .env file loading."""

    def test_load_env_valid(self) -> None:
        """Test loading valid .env file."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.write("# Comment\n")
            f.write("KEY3=value3\n")
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "env")
            assert result["KEY1"] == "value1"
            assert result["KEY2"] == "value2"
            assert result["KEY3"] == "value3"
        finally:
            path.unlink()

    def test_load_env_empty_file(self) -> None:
        """Test loading empty .env file."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".env") as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            result = loader.load(path, "env")
            assert result == {}
        finally:
            path.unlink()


class TestConfigFileLoaderErrors:
    """Test error handling."""

    def test_load_unsupported_format(self) -> None:
        """Test loading unsupported format."""
        loader = ConfigFileLoader()

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("data")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                loader.load(path, "unsupported")
            assert "Unsupported format" in str(exc_info.value)
        finally:
            path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading nonexistent file."""
        loader = ConfigFileLoader()
        path = Path("/nonexistent/file.json")

        with pytest.raises(ConfigurationError) as exc_info:
            loader.load(path, "json")
        assert "Error reading config file" in str(exc_info.value)

    def test_save_unsupported_format(self) -> None:
        """Test saving unsupported format."""
        loader = ConfigFileLoader()
        data = {"key": "value"}

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.txt"
            result = loader.save(path, data, "txt")
            assert result is False

    def test_save_creates_parent_directories(self) -> None:
        """Test save creates parent directories."""
        loader = ConfigFileLoader()
        data = {"key": "value"}

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dirs" / "config.json"
            result = loader.save(path, data, "json")
            assert result is True
            assert path.exists()
            assert path.parent.exists()
