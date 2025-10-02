"""Tests for design tokens."""

from __future__ import annotations

from qtframework.themes.tokens import (
    BorderRadius,
    ComponentColors,
    DesignTokens,
    PrimitiveColors,
    SemanticColors,
    Shadows,
    Spacing,
    SyntaxColors,
    Transitions,
    Typography,
)


class TestPrimitiveColors:
    """Test primitive color tokens."""

    def test_default_colors(self) -> None:
        """Test default color values are set."""
        colors = PrimitiveColors()
        assert colors.gray_50 == "#FAFAFA"
        assert colors.primary_500 == "#2196F3"
        assert colors.white == "#FFFFFF"
        assert colors.black == "#000000"


class TestSemanticColors:
    """Test semantic color tokens."""

    def test_default_values(self) -> None:
        """Test semantic colors have default values."""
        colors = SemanticColors()
        assert colors.bg_primary == ""
        assert colors.fg_primary == ""
        assert colors.action_primary == ""


class TestComponentColors:
    """Test component color tokens."""

    def test_default_values(self) -> None:
        """Test component colors have default values."""
        colors = ComponentColors()
        assert colors.button_primary_bg == ""
        assert colors.input_bg == ""
        assert colors.table_header_bg == ""


class TestTypography:
    """Test typography tokens."""

    def test_default_font_families(self) -> None:
        """Test default font families."""
        typo = Typography()
        assert "Segoe UI" in typo.font_family_default
        assert "Cascadia Code" in typo.font_family_mono
        assert typo.font_family_code == "Consolas"

    def test_font_sizes(self) -> None:
        """Test font size tokens."""
        typo = Typography()
        assert typo.font_size_xs == 11
        assert typo.font_size_md == 14
        assert typo.font_size_5xl == 32

    def test_font_weights(self) -> None:
        """Test font weight tokens."""
        typo = Typography()
        assert typo.font_weight_thin == 100
        assert typo.font_weight_normal == 400
        assert typo.font_weight_black == 900

    def test_line_heights(self) -> None:
        """Test line height tokens."""
        typo = Typography()
        assert typo.line_height_tight == 1.2
        assert typo.line_height_normal == 1.5
        assert typo.line_height_loose == 2.0


class TestSpacing:
    """Test spacing tokens."""

    def test_spacing_scale(self) -> None:
        """Test spacing scale values."""
        spacing = Spacing()
        assert spacing.space_0 == 0
        assert spacing.space_4 == 8
        assert spacing.space_32 == 64


class TestBorderRadius:
    """Test border radius tokens."""

    def test_radius_values(self) -> None:
        """Test border radius values."""
        borders = BorderRadius()
        assert borders.radius_none == 0
        assert borders.radius_md == 4
        assert borders.radius_full == 9999


class TestShadows:
    """Test shadow tokens."""

    def test_shadow_values(self) -> None:
        """Test shadow values."""
        shadows = Shadows()
        assert shadows.shadow_none == "none"
        assert "rgba" in shadows.shadow_md
        assert "rgba" in shadows.shadow_xl


class TestTransitions:
    """Test transition tokens."""

    def test_transition_values(self) -> None:
        """Test transition values."""
        transitions = Transitions()
        assert transitions.transition_fast == "150ms ease-in-out"
        assert transitions.transition_normal == "250ms ease-in-out"
        assert transitions.transition_slow == "350ms ease-in-out"


class TestSyntaxColors:
    """Test syntax highlighting color tokens."""

    def test_default_syntax_colors(self) -> None:
        """Test default syntax colors."""
        syntax = SyntaxColors()
        assert syntax.keyword == "#0000FF"
        assert syntax.string == "#A31515"
        assert syntax.comment == "#008000"


class TestDesignTokens:
    """Test complete design token system."""

    def test_initialization(self) -> None:
        """Test DesignTokens initializes all token categories."""
        tokens = DesignTokens()
        assert isinstance(tokens.primitive, PrimitiveColors)
        assert isinstance(tokens.semantic, SemanticColors)
        assert isinstance(tokens.components, ComponentColors)
        assert isinstance(tokens.typography, Typography)
        assert isinstance(tokens.spacing, Spacing)
        assert isinstance(tokens.borders, BorderRadius)
        assert isinstance(tokens.shadows, Shadows)
        assert isinstance(tokens.transitions, Transitions)
        assert isinstance(tokens.syntax, SyntaxColors)

    def test_apply_font_scale_100(self) -> None:
        """Test font scale at 100% doesn't change values."""
        tokens = DesignTokens()
        original_md = tokens.typography.font_size_md

        tokens.apply_font_scale(100)
        assert tokens.typography.font_size_md == original_md

    def test_apply_font_scale_125(self) -> None:
        """Test font scale at 125%."""
        tokens = DesignTokens()
        original_md = tokens.typography.font_size_md

        tokens.apply_font_scale(125)
        assert tokens.typography.font_size_md == int(original_md * 1.25)

    def test_apply_font_scale_150(self) -> None:
        """Test font scale at 150%."""
        tokens = DesignTokens()
        original_xs = 11
        original_5xl = 32

        tokens.apply_font_scale(150)
        assert tokens.typography.font_size_xs == int(original_xs * 1.5)
        assert tokens.typography.font_size_5xl == int(original_5xl * 1.5)

    def test_apply_font_scale_all_sizes(self) -> None:
        """Test font scale affects all font sizes."""
        tokens = DesignTokens()
        tokens.apply_font_scale(200)

        assert tokens.typography.font_size_xs == 22
        assert tokens.typography.font_size_sm == 24
        assert tokens.typography.font_size_md == 28
        assert tokens.typography.font_size_lg == 32
        assert tokens.typography.font_size_xl == 36
        assert tokens.typography.font_size_2xl == 40
        assert tokens.typography.font_size_3xl == 48
        assert tokens.typography.font_size_4xl == 56
        assert tokens.typography.font_size_5xl == 64

    def test_resolve_token_primitive(self) -> None:
        """Test resolving primitive token paths."""
        tokens = DesignTokens()
        value = tokens.resolve_token("primitive.primary_500")
        assert value == "#2196F3"

    def test_resolve_token_typography(self) -> None:
        """Test resolving typography token paths."""
        tokens = DesignTokens()
        value = tokens.resolve_token("typography.font_size_md")
        assert value == "14"

    def test_resolve_token_spacing(self) -> None:
        """Test resolving spacing token paths."""
        tokens = DesignTokens()
        value = tokens.resolve_token("spacing.space_4")
        assert value == "8"

    def test_resolve_token_invalid_path(self) -> None:
        """Test resolving invalid token path returns None."""
        tokens = DesignTokens()
        value = tokens.resolve_token("invalid.path.to.token")
        assert value is None

    def test_resolve_token_partial_path(self) -> None:
        """Test resolving partial token path returns None."""
        tokens = DesignTokens()
        value = tokens.resolve_token("primitive.nonexistent")
        assert value is None

    def test_resolve_semantic_colors(self) -> None:
        """Test resolving semantic color references."""
        tokens = DesignTokens()
        tokens.semantic.bg_primary = "{primitive.gray_50}"

        tokens.resolve_semantic_colors()
        assert tokens.semantic.bg_primary == "#FAFAFA"

    def test_resolve_semantic_colors_multiple(self) -> None:
        """Test resolving multiple semantic color references."""
        tokens = DesignTokens()
        tokens.semantic.bg_primary = "{primitive.gray_50}"
        tokens.semantic.fg_primary = "{primitive.gray_900}"
        tokens.semantic.action_primary = "{primitive.primary_500}"

        tokens.resolve_semantic_colors()
        assert tokens.semantic.bg_primary == "#FAFAFA"
        assert tokens.semantic.fg_primary == "#212121"
        assert tokens.semantic.action_primary == "#2196F3"

    def test_resolve_semantic_colors_invalid_reference(self) -> None:
        """Test resolving invalid semantic color reference keeps original."""
        tokens = DesignTokens()
        tokens.semantic.bg_primary = "{invalid.token}"

        tokens.resolve_semantic_colors()
        assert tokens.semantic.bg_primary == "{invalid.token}"

    def test_to_dict(self) -> None:
        """Test converting tokens to dictionary."""
        tokens = DesignTokens()
        data = tokens.to_dict()

        assert "primitive" in data
        assert "semantic" in data
        assert "components" in data
        assert "typography" in data
        assert "spacing" in data
        assert "borders" in data
        assert "shadows" in data
        assert "transitions" in data
        assert "syntax" in data

        assert isinstance(data["primitive"], dict)
        assert "primary_500" in data["primitive"]
        assert data["primitive"]["primary_500"] == "#2196F3"

    def test_from_dict(self) -> None:
        """Test creating tokens from dictionary."""
        data = {
            "primitive": {
                "primary_500": "#FF0000",
            },
            "typography": {
                "font_size_md": 16,
            },
        }

        tokens = DesignTokens.from_dict(data)
        assert tokens.primitive.primary_500 == "#FF0000"
        assert tokens.typography.font_size_md == 16

    def test_from_dict_partial(self) -> None:
        """Test creating tokens from partial dictionary uses defaults."""
        data = {
            "primitive": {
                "primary_500": "#FF0000",
            },
        }

        tokens = DesignTokens.from_dict(data)
        assert tokens.primitive.primary_500 == "#FF0000"
        assert tokens.typography.font_size_md == 14  # Default

    def test_round_trip_to_from_dict(self) -> None:
        """Test round-trip conversion to/from dict."""
        tokens1 = DesignTokens()
        tokens1.primitive.primary_500 = "#123456"
        tokens1.typography.font_size_md = 20

        data = tokens1.to_dict()
        tokens2 = DesignTokens.from_dict(data)

        assert tokens2.primitive.primary_500 == "#123456"
        assert tokens2.typography.font_size_md == 20

    def test_resolve_token_with_dict_attribute(self) -> None:
        """Test resolving token path that goes through a dict attribute."""
        tokens = DesignTokens()
        # Manually add a custom dict attribute to test the dict branch
        tokens.custom_dict = {"nested": {"value": "test_value"}}  # type: ignore[attr-defined]

        # Try to resolve through the dict
        value = tokens.resolve_token("custom_dict.nested.value")
        assert value == "test_value"
