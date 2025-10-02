"""Design token system for theming."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


class PrimitiveColors(BaseModel):
    """Primitive color tokens - raw color values."""

    # Grayscale
    gray_50: str = Field(default="#FAFAFA")
    gray_100: str = Field(default="#F5F5F5")
    gray_200: str = Field(default="#EEEEEE")
    gray_300: str = Field(default="#E0E0E0")
    gray_400: str = Field(default="#BDBDBD")
    gray_500: str = Field(default="#9E9E9E")
    gray_600: str = Field(default="#757575")
    gray_700: str = Field(default="#616161")
    gray_800: str = Field(default="#424242")
    gray_900: str = Field(default="#212121")
    gray_950: str = Field(default="#121212")

    # Primary colors (Blue by default)
    primary_50: str = Field(default="#E3F2FD")
    primary_100: str = Field(default="#BBDEFB")
    primary_200: str = Field(default="#90CAF9")
    primary_300: str = Field(default="#64B5F6")
    primary_400: str = Field(default="#42A5F5")
    primary_500: str = Field(default="#2196F3")
    primary_600: str = Field(default="#1E88E5")
    primary_700: str = Field(default="#1976D2")
    primary_800: str = Field(default="#1565C0")
    primary_900: str = Field(default="#0D47A1")
    primary_950: str = Field(default="#0A3A7F")

    # Secondary colors (Amber by default)
    secondary_50: str = Field(default="#FFF8E1")
    secondary_100: str = Field(default="#FFECB3")
    secondary_200: str = Field(default="#FFE082")
    secondary_300: str = Field(default="#FFD54F")
    secondary_400: str = Field(default="#FFCA28")
    secondary_500: str = Field(default="#FFC107")
    secondary_600: str = Field(default="#FFB300")
    secondary_700: str = Field(default="#FFA000")
    secondary_800: str = Field(default="#FF8F00")
    secondary_900: str = Field(default="#FF6F00")
    secondary_950: str = Field(default="#E65100")

    # Success (Green)
    success_50: str = Field(default="#E8F5E9")
    success_100: str = Field(default="#C8E6C9")
    success_200: str = Field(default="#A5D6A7")
    success_300: str = Field(default="#81C784")
    success_400: str = Field(default="#66BB6A")
    success_500: str = Field(default="#4CAF50")
    success_600: str = Field(default="#43A047")
    success_700: str = Field(default="#388E3C")
    success_800: str = Field(default="#2E7D32")
    success_900: str = Field(default="#1B5E20")
    success_950: str = Field(default="#0D4018")

    # Warning (Orange)
    warning_50: str = Field(default="#FFF3E0")
    warning_100: str = Field(default="#FFE0B2")
    warning_200: str = Field(default="#FFCC80")
    warning_300: str = Field(default="#FFB74D")
    warning_400: str = Field(default="#FFA726")
    warning_500: str = Field(default="#FF9800")
    warning_600: str = Field(default="#FB8C00")
    warning_700: str = Field(default="#F57C00")
    warning_800: str = Field(default="#EF6C00")
    warning_900: str = Field(default="#E65100")
    warning_950: str = Field(default="#BF360C")

    # Error (Red)
    error_50: str = Field(default="#FFEBEE")
    error_100: str = Field(default="#FFCDD2")
    error_200: str = Field(default="#EF9A9A")
    error_300: str = Field(default="#E57373")
    error_400: str = Field(default="#EF5350")
    error_500: str = Field(default="#F44336")
    error_600: str = Field(default="#E53935")
    error_700: str = Field(default="#D32F2F")
    error_800: str = Field(default="#C62828")
    error_900: str = Field(default="#B71C1C")
    error_950: str = Field(default="#7F0000")

    # Info (Cyan)
    info_50: str = Field(default="#E0F7FA")
    info_100: str = Field(default="#B2EBF2")
    info_200: str = Field(default="#80DEEA")
    info_300: str = Field(default="#4DD0E1")
    info_400: str = Field(default="#26C6DA")
    info_500: str = Field(default="#00BCD4")
    info_600: str = Field(default="#00ACC1")
    info_700: str = Field(default="#0097A7")
    info_800: str = Field(default="#00838F")
    info_900: str = Field(default="#006064")
    info_950: str = Field(default="#004D50")

    # Pure colors
    white: str = Field(default="#FFFFFF")
    black: str = Field(default="#000000")
    transparent: str = Field(default="transparent")


class SemanticColors(BaseModel):
    """Semantic color tokens - meaning-based references."""

    # Background
    bg_primary: str = Field(default="")  # Main background
    bg_secondary: str = Field(default="")  # Secondary surfaces
    bg_tertiary: str = Field(default="")  # Tertiary surfaces
    bg_elevated: str = Field(default="")  # Elevated surfaces (cards, dialogs)
    bg_overlay: str = Field(default="")  # Overlay background

    # Foreground/Text
    fg_primary: str = Field(default="")  # Primary text
    fg_secondary: str = Field(default="")  # Secondary text
    fg_tertiary: str = Field(default="")  # Tertiary/disabled text
    fg_on_accent: str = Field(default="")  # Text on accent colors
    fg_on_dark: str = Field(default="")  # Text on dark backgrounds
    fg_on_light: str = Field(default="")  # Text on light backgrounds

    # Interactive states
    action_primary: str = Field(default="")  # Primary action color
    action_primary_hover: str = Field(default="")
    action_primary_active: str = Field(default="")
    action_secondary: str = Field(default="")  # Secondary action color
    action_secondary_hover: str = Field(default="")
    action_secondary_active: str = Field(default="")

    # Feedback
    feedback_success: str = Field(default="")
    feedback_warning: str = Field(default="")
    feedback_error: str = Field(default="")
    feedback_info: str = Field(default="")

    # Borders
    border_default: str = Field(default="")
    border_subtle: str = Field(default="")
    border_strong: str = Field(default="")
    border_focus: str = Field(default="")

    # Special states
    state_hover: str = Field(default="")
    state_selected: str = Field(default="")
    state_disabled: str = Field(default="")
    state_focus: str = Field(default="")


class ComponentColors(BaseModel):
    """Component-specific color tokens."""

    # Button
    button_primary_bg: str = Field(default="")
    button_primary_fg: str = Field(default="")
    button_primary_border: str = Field(default="")
    button_secondary_bg: str = Field(default="")
    button_secondary_fg: str = Field(default="")
    button_secondary_border: str = Field(default="")

    # Input
    input_bg: str = Field(default="")
    input_fg: str = Field(default="")
    input_border: str = Field(default="")
    input_placeholder: str = Field(default="")

    # Table
    table_header_bg: str = Field(default="")
    table_header_fg: str = Field(default="")
    table_row_bg: str = Field(default="")
    table_row_bg_alt: str = Field(default="")
    table_row_hover: str = Field(default="")
    table_row_selected: str = Field(default="")
    table_border: str = Field(default="")

    # Menu
    menu_bg: str = Field(default="")
    menu_fg: str = Field(default="")
    menu_hover_bg: str = Field(default="")
    menu_hover_fg: str = Field(default="")
    menu_selected_bg: str = Field(default="")
    menu_selected_fg: str = Field(default="")

    # Scrollbar
    scrollbar_bg: str = Field(default="")
    scrollbar_thumb: str = Field(default="")
    scrollbar_thumb_hover: str = Field(default="")

    # Tab
    tab_bg: str = Field(default="")
    tab_fg: str = Field(default="")
    tab_active_bg: str = Field(default="")
    tab_active_fg: str = Field(default="")
    tab_hover_bg: str = Field(default="")
    tab_hover_fg: str = Field(default="")

    # Chart/Graph colors
    chart_1: str = Field(default="")
    chart_2: str = Field(default="")
    chart_3: str = Field(default="")
    chart_4: str = Field(default="")
    chart_5: str = Field(default="")
    chart_6: str = Field(default="")
    chart_grid: str = Field(default="")
    chart_axis: str = Field(default="")

    # Badge colors
    badge_default_bg: str = Field(default="")
    badge_default_fg: str = Field(default="")
    badge_default_border: str = Field(default="")

    badge_primary_bg: str = Field(default="")
    badge_primary_fg: str = Field(default="")
    badge_primary_border: str = Field(default="")

    badge_secondary_bg: str = Field(default="")
    badge_secondary_fg: str = Field(default="")
    badge_secondary_border: str = Field(default="")

    badge_success_bg: str = Field(default="")
    badge_success_fg: str = Field(default="")
    badge_success_border: str = Field(default="")

    badge_warning_bg: str = Field(default="")
    badge_warning_fg: str = Field(default="")
    badge_warning_border: str = Field(default="")

    badge_danger_bg: str = Field(default="")
    badge_danger_fg: str = Field(default="")
    badge_danger_border: str = Field(default="")

    badge_info_bg: str = Field(default="")
    badge_info_fg: str = Field(default="")
    badge_info_border: str = Field(default="")

    badge_light_bg: str = Field(default="")
    badge_light_fg: str = Field(default="")
    badge_light_border: str = Field(default="")

    badge_dark_bg: str = Field(default="")
    badge_dark_fg: str = Field(default="")
    badge_dark_border: str = Field(default="")


class Typography(BaseModel):
    """Typography tokens."""

    # Font families
    font_family_default: str = Field(
        default="'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica', sans-serif"
    )
    font_family_mono: str = Field(
        default="'Cascadia Code', 'Consolas', 'Monaco', 'Courier New', monospace"
    )
    font_family_code: str = Field(
        default="Consolas"  # Single font name for Qt QFont
    )

    # Font sizes
    font_size_xs: int = Field(default=11)
    font_size_sm: int = Field(default=12)
    font_size_md: int = Field(default=14)
    font_size_lg: int = Field(default=16)
    font_size_xl: int = Field(default=18)
    font_size_2xl: int = Field(default=20)
    font_size_3xl: int = Field(default=24)
    font_size_4xl: int = Field(default=28)
    font_size_5xl: int = Field(default=32)

    # Font weights
    font_weight_thin: int = Field(default=100)
    font_weight_light: int = Field(default=300)
    font_weight_normal: int = Field(default=400)
    font_weight_medium: int = Field(default=500)
    font_weight_semibold: int = Field(default=600)
    font_weight_bold: int = Field(default=700)
    font_weight_black: int = Field(default=900)

    # Line heights
    line_height_tight: float = Field(default=1.2)
    line_height_normal: float = Field(default=1.5)
    line_height_relaxed: float = Field(default=1.75)
    line_height_loose: float = Field(default=2.0)


class Spacing(BaseModel):
    """Spacing tokens."""

    space_0: int = Field(default=0)
    space_1: int = Field(default=2)
    space_2: int = Field(default=4)
    space_3: int = Field(default=6)
    space_4: int = Field(default=8)
    space_5: int = Field(default=10)
    space_6: int = Field(default=12)
    space_8: int = Field(default=16)
    space_10: int = Field(default=20)
    space_12: int = Field(default=24)
    space_16: int = Field(default=32)
    space_20: int = Field(default=40)
    space_24: int = Field(default=48)
    space_32: int = Field(default=64)


class BorderRadius(BaseModel):
    """Border radius tokens."""

    radius_none: int = Field(default=0)
    radius_sm: int = Field(default=2)
    radius_md: int = Field(default=4)
    radius_lg: int = Field(default=6)
    radius_xl: int = Field(default=8)
    radius_2xl: int = Field(default=12)
    radius_3xl: int = Field(default=16)
    radius_full: int = Field(default=9999)


class Shadows(BaseModel):
    """Shadow tokens."""

    shadow_none: str = Field(default="none")
    shadow_sm: str = Field(default="0 1px 2px 0 rgba(0, 0, 0, 0.05)")
    shadow_md: str = Field(default="0 4px 6px -1px rgba(0, 0, 0, 0.1)")
    shadow_lg: str = Field(default="0 10px 15px -3px rgba(0, 0, 0, 0.1)")
    shadow_xl: str = Field(default="0 20px 25px -5px rgba(0, 0, 0, 0.1)")
    shadow_2xl: str = Field(default="0 25px 50px -12px rgba(0, 0, 0, 0.25)")
    shadow_inner: str = Field(default="inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)")


class Transitions(BaseModel):
    """Transition/animation tokens."""

    transition_fast: str = Field(default="150ms ease-in-out")
    transition_normal: str = Field(default="250ms ease-in-out")
    transition_slow: str = Field(default="350ms ease-in-out")


class SyntaxColors(BaseModel):
    """Syntax highlighting color tokens."""

    # Core syntax elements
    keyword: str = Field(default="#0000FF")
    class_name: str = Field(default="#267F99")
    function: str = Field(default="#795E26")
    string: str = Field(default="#A31515")
    comment: str = Field(default="#008000")
    number: str = Field(default="#098658")
    operator: str = Field(default="#000000")

    # Additional elements
    decorator: str = Field(default="#AA0000")
    constant: str = Field(default="#0000FF")
    variable: str = Field(default="#001080")
    parameter: str = Field(default="#001080")
    type: str = Field(default="#267F99")
    namespace: str = Field(default="#267F99")

    # Special
    error: str = Field(default="#FF0000")
    warning: str = Field(default="#FFA500")
    info: str = Field(default="#0000FF")


@dataclass
class DesignTokens:
    """Complete design token system."""

    primitive: PrimitiveColors = field(default_factory=PrimitiveColors)
    semantic: SemanticColors = field(default_factory=SemanticColors)
    components: ComponentColors = field(default_factory=ComponentColors)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    borders: BorderRadius = field(default_factory=BorderRadius)
    shadows: Shadows = field(default_factory=Shadows)
    transitions: Transitions = field(default_factory=Transitions)
    syntax: SyntaxColors = field(default_factory=SyntaxColors)

    def apply_font_scale(self, scale_percent: int = 100) -> None:
        """Apply font scaling to all typography tokens.

        Args:
            scale_percent: Percentage to scale fonts (e.g., 100 = normal, 125 = 125%, 150 = 150%)
        """
        if scale_percent == 100:
            return  # No scaling needed

        scale_factor = scale_percent / 100.0

        # Scale all font sizes
        self.typography.font_size_xs = int(self.typography.font_size_xs * scale_factor)
        self.typography.font_size_sm = int(self.typography.font_size_sm * scale_factor)
        self.typography.font_size_md = int(self.typography.font_size_md * scale_factor)
        self.typography.font_size_lg = int(self.typography.font_size_lg * scale_factor)
        self.typography.font_size_xl = int(self.typography.font_size_xl * scale_factor)
        self.typography.font_size_2xl = int(self.typography.font_size_2xl * scale_factor)
        self.typography.font_size_3xl = int(self.typography.font_size_3xl * scale_factor)
        self.typography.font_size_4xl = int(self.typography.font_size_4xl * scale_factor)
        self.typography.font_size_5xl = int(self.typography.font_size_5xl * scale_factor)

    def resolve_token(self, token_path: str) -> str | None:
        """Resolve a token path to its value.

        Args:
            token_path: Dot-separated path to token (e.g., "primitive.primary_500")

        Returns:
            Token value or None if not found
        """
        parts = token_path.split(".")
        current: Any = self

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return str(current) if current is not None else None

    def resolve_semantic_colors(self) -> None:
        """Resolve semantic color references to actual values."""
        # This method would resolve semantic tokens that reference primitive tokens
        # For example, if semantic.bg_primary = "{primitive.gray_50}"
        # It would resolve it to the actual color value
        for attr_name in dir(self.semantic):
            if not attr_name.startswith("_"):
                value = getattr(self.semantic, attr_name)
                if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                    token_path = value[1:-1]  # Remove braces
                    resolved = self.resolve_token(token_path)
                    if resolved:
                        setattr(self.semantic, attr_name, resolved)

    def to_dict(self) -> dict[str, Any]:
        """Convert tokens to dictionary format."""
        return {
            "primitive": self.primitive.model_dump(),
            "semantic": self.semantic.model_dump(),
            "components": self.components.model_dump(),
            "typography": self.typography.model_dump(),
            "spacing": self.spacing.model_dump(),
            "borders": self.borders.model_dump(),
            "shadows": self.shadows.model_dump(),
            "transitions": self.transitions.model_dump(),
            "syntax": self.syntax.model_dump(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesignTokens:
        """Create DesignTokens from dictionary."""
        return cls(
            primitive=PrimitiveColors(**data.get("primitive", {})),
            semantic=SemanticColors(**data.get("semantic", {})),
            components=ComponentColors(**data.get("components", {})),
            typography=Typography(**data.get("typography", {})),
            spacing=Spacing(**data.get("spacing", {})),
            borders=BorderRadius(**data.get("borders", {})),
            shadows=Shadows(**data.get("shadows", {})),
            transitions=Transitions(**data.get("transitions", {})),
            syntax=SyntaxColors(**data.get("syntax", {})),
        )
