"""Built-in themes using the modern token system."""

from __future__ import annotations

from qtframework.themes.theme import Theme
from qtframework.themes.tokens import (ComponentColors, DesignTokens,
                                       PrimitiveColors, SemanticColors,
                                       SyntaxColors, Typography)


def create_light_theme() -> Theme:
    """Create the built-in light theme."""
    tokens = DesignTokens()

    # Use default primitive colors (already set for light theme)

    # Configure semantic colors for light theme
    tokens.semantic = SemanticColors(
        # Background
        bg_primary=tokens.primitive.white,
        bg_secondary=tokens.primitive.gray_50,
        bg_tertiary=tokens.primitive.gray_100,
        bg_elevated=tokens.primitive.white,
        bg_overlay="rgba(0, 0, 0, 0.5)",

        # Foreground/Text
        fg_primary=tokens.primitive.gray_900,
        fg_secondary=tokens.primitive.gray_600,
        fg_tertiary=tokens.primitive.gray_400,
        fg_on_accent=tokens.primitive.white,
        fg_on_dark=tokens.primitive.white,
        fg_on_light=tokens.primitive.gray_900,

        # Interactive states
        action_primary=tokens.primitive.primary_500,
        action_primary_hover=tokens.primitive.primary_600,
        action_primary_active=tokens.primitive.primary_700,
        action_secondary=tokens.primitive.secondary_500,
        action_secondary_hover=tokens.primitive.secondary_600,
        action_secondary_active=tokens.primitive.secondary_700,

        # Feedback
        feedback_success=tokens.primitive.success_500,
        feedback_warning=tokens.primitive.warning_500,
        feedback_error=tokens.primitive.error_500,
        feedback_info=tokens.primitive.info_500,

        # Borders
        border_default=tokens.primitive.gray_300,
        border_subtle=tokens.primitive.gray_200,
        border_strong=tokens.primitive.gray_400,
        border_focus=tokens.primitive.primary_500,

        # Special states
        state_hover=tokens.primitive.gray_100,
        state_selected=tokens.primitive.primary_100,
        state_disabled=tokens.primitive.gray_100,
        state_focus=tokens.primitive.primary_100,
    )

    # Configure component colors for light theme
    tokens.components = ComponentColors(
        # Button
        button_primary_bg=tokens.primitive.primary_500,
        button_primary_fg=tokens.primitive.white,
        button_primary_border=tokens.primitive.primary_500,
        button_secondary_bg=tokens.primitive.gray_100,
        button_secondary_fg=tokens.primitive.gray_900,
        button_secondary_border=tokens.primitive.gray_300,

        # Input
        input_bg=tokens.primitive.white,
        input_fg=tokens.primitive.gray_900,
        input_border=tokens.primitive.gray_300,
        input_placeholder=tokens.primitive.gray_500,

        # Table
        table_header_bg=tokens.primitive.gray_100,
        table_header_fg=tokens.primitive.gray_900,
        table_row_bg=tokens.primitive.white,
        table_row_bg_alt=tokens.primitive.gray_50,
        table_row_hover=tokens.primitive.gray_100,
        table_row_selected=tokens.primitive.primary_100,
        table_border=tokens.primitive.gray_200,

        # Menu
        menu_bg=tokens.primitive.white,
        menu_fg=tokens.primitive.gray_900,
        menu_hover_bg=tokens.primitive.gray_100,
        menu_hover_fg=tokens.primitive.gray_900,
        menu_selected_bg=tokens.primitive.primary_100,
        menu_selected_fg=tokens.primitive.primary_700,

        # Scrollbar
        scrollbar_bg=tokens.primitive.gray_100,
        scrollbar_thumb=tokens.primitive.gray_400,
        scrollbar_thumb_hover=tokens.primitive.gray_500,

        # Tab
        tab_bg=tokens.primitive.gray_100,
        tab_fg=tokens.primitive.gray_600,
        tab_active_bg=tokens.primitive.white,
        tab_active_fg=tokens.primitive.primary_500,
        tab_hover_bg=tokens.primitive.gray_50,
        tab_hover_fg=tokens.primitive.gray_900,

        # Chart/Graph colors
        chart_1=tokens.primitive.primary_500,
        chart_2=tokens.primitive.success_500,
        chart_3=tokens.primitive.warning_500,
        chart_4=tokens.primitive.error_500,
        chart_5="#9C27B0",  # Purple
        chart_6="#00BCD4",  # Cyan
        chart_grid=tokens.primitive.gray_200,
        chart_axis=tokens.primitive.gray_600,
    )

    # Configure typography for light theme
    tokens.typography = Typography(
        font_family_code="Consolas"  # Windows default monospace
    )

    # Configure syntax highlighting colors for light theme
    tokens.syntax = SyntaxColors(
        keyword="#0000FF",  # Blue
        class_name="#267F99",  # Teal
        function="#795E26",  # Brown
        string="#A31515",  # Red
        comment="#008000",  # Green
        number="#098658",  # Dark green
        operator="#000000",  # Black
        decorator="#AA0000",  # Dark red
        constant="#0000FF",  # Blue
        variable="#001080",  # Dark blue
        parameter="#001080",  # Dark blue
        type="#267F99",  # Teal
        namespace="#267F99",  # Teal
        error="#FF0000",  # Red
        warning="#FFA500",  # Orange
        info="#0000FF",  # Blue
    )

    return Theme(
        name="light",
        display_name="Light",
        description="Clean and modern light theme",
        author="Qt Framework",
        version="2.0.0",
        tokens=tokens,
    )


def create_dark_theme() -> Theme:
    """Create the built-in dark theme."""
    tokens = DesignTokens()

    # Override primitive colors for dark theme
    tokens.primitive = PrimitiveColors(
        # Grayscale - inverted for dark theme
        gray_50="#121212",
        gray_100="#1E1E1E",
        gray_200="#2D2D2D",
        gray_300="#404040",
        gray_400="#525252",
        gray_500="#666666",
        gray_600="#808080",
        gray_700="#9E9E9E",
        gray_800="#B0B0B0",
        gray_900="#E0E0E0",
        gray_950="#F5F5F5",

        # Primary colors - slightly adjusted for dark theme
        primary_50="#0A1929",
        primary_100="#0F2942",
        primary_200="#173A5E",
        primary_300="#1E4976",
        primary_400="#2196F3",
        primary_500="#42A5F5",
        primary_600="#64B5F6",
        primary_700="#90CAF9",
        primary_800="#BBDEFB",
        primary_900="#E3F2FD",
        primary_950="#F0F7FF",

        # Keep other color scales similar
        secondary_50="#1A0E00",
        secondary_100="#2E1A00",
        secondary_200="#422500",
        secondary_300="#573300",
        secondary_400="#6B3E00",
        secondary_500="#FFA726",
        secondary_600="#FFB74D",
        secondary_700="#FFCC80",
        secondary_800="#FFE0B2",
        secondary_900="#FFF3E0",
        secondary_950="#FFF8E1",

        # Success
        success_50="#0D2818",
        success_100="#1B5E20",
        success_200="#2E7D32",
        success_300="#388E3C",
        success_400="#43A047",
        success_500="#4CAF50",
        success_600="#66BB6A",
        success_700="#81C784",
        success_800="#A5D6A7",
        success_900="#C8E6C9",
        success_950="#E8F5E9",

        # Warning
        warning_50="#331400",
        warning_100="#4D1F00",
        warning_200="#662900",
        warning_300="#803300",
        warning_400="#993D00",
        warning_500="#FF9800",
        warning_600="#FFA726",
        warning_700="#FFB74D",
        warning_800="#FFCC80",
        warning_900="#FFE0B2",
        warning_950="#FFF3E0",

        # Error
        error_50="#4A0E0E",
        error_100="#7F1D1D",
        error_200="#991B1B",
        error_300="#B91C1C",
        error_400="#DC2626",
        error_500="#EF4444",
        error_600="#F87171",
        error_700="#FCA5A5",
        error_800="#FECACA",
        error_900="#FEE2E2",
        error_950="#FEF2F2",

        # Info
        info_50="#002838",
        info_100="#003D4D",
        info_200="#005566",
        info_300="#006B80",
        info_400="#008299",
        info_500="#00ACC1",
        info_600="#26C6DA",
        info_700="#4DD0E1",
        info_800="#80DEEA",
        info_900="#B2EBF2",
        info_950="#E0F7FA",

        # Pure colors
        white="#FFFFFF",
        black="#000000",
        transparent="transparent",
    )

    # Configure semantic colors for dark theme
    tokens.semantic = SemanticColors(
        # Background
        bg_primary=tokens.primitive.gray_100,
        bg_secondary=tokens.primitive.gray_200,
        bg_tertiary=tokens.primitive.gray_300,
        bg_elevated=tokens.primitive.gray_200,
        bg_overlay="rgba(0, 0, 0, 0.7)",

        # Foreground/Text
        fg_primary=tokens.primitive.gray_900,
        fg_secondary=tokens.primitive.gray_700,
        fg_tertiary=tokens.primitive.gray_500,
        fg_on_accent=tokens.primitive.white,
        fg_on_dark=tokens.primitive.white,
        fg_on_light=tokens.primitive.gray_50,

        # Interactive states
        action_primary=tokens.primitive.primary_500,
        action_primary_hover=tokens.primitive.primary_600,
        action_primary_active=tokens.primitive.primary_700,
        action_secondary=tokens.primitive.secondary_500,
        action_secondary_hover=tokens.primitive.secondary_600,
        action_secondary_active=tokens.primitive.secondary_700,

        # Feedback
        feedback_success=tokens.primitive.success_500,
        feedback_warning=tokens.primitive.warning_500,
        feedback_error=tokens.primitive.error_500,
        feedback_info=tokens.primitive.info_500,

        # Borders
        border_default=tokens.primitive.gray_400,
        border_subtle=tokens.primitive.gray_300,
        border_strong=tokens.primitive.gray_500,
        border_focus=tokens.primitive.primary_500,

        # Special states
        state_hover=tokens.primitive.gray_300,
        state_selected=tokens.primitive.primary_300,
        state_disabled=tokens.primitive.gray_200,
        state_focus=tokens.primitive.primary_300,
    )

    # Configure component colors for dark theme
    tokens.components = ComponentColors(
        # Button
        button_primary_bg=tokens.primitive.primary_500,
        button_primary_fg=tokens.primitive.white,
        button_primary_border=tokens.primitive.primary_500,
        button_secondary_bg=tokens.primitive.gray_300,
        button_secondary_fg=tokens.primitive.gray_900,
        button_secondary_border=tokens.primitive.gray_400,

        # Input
        input_bg=tokens.primitive.gray_200,
        input_fg=tokens.primitive.gray_900,
        input_border=tokens.primitive.gray_400,
        input_placeholder=tokens.primitive.gray_600,

        # Table
        table_header_bg=tokens.primitive.gray_300,
        table_header_fg=tokens.primitive.gray_900,
        table_row_bg=tokens.primitive.gray_100,
        table_row_bg_alt=tokens.primitive.gray_200,
        table_row_hover=tokens.primitive.gray_300,
        table_row_selected=tokens.primitive.primary_300,
        table_border=tokens.primitive.gray_400,

        # Menu
        menu_bg=tokens.primitive.gray_200,
        menu_fg=tokens.primitive.gray_900,
        menu_hover_bg=tokens.primitive.gray_300,
        menu_hover_fg=tokens.primitive.gray_900,
        menu_selected_bg=tokens.primitive.primary_300,
        menu_selected_fg=tokens.primitive.white,

        # Scrollbar
        scrollbar_bg=tokens.primitive.gray_200,
        scrollbar_thumb=tokens.primitive.gray_500,
        scrollbar_thumb_hover=tokens.primitive.gray_600,

        # Tab
        tab_bg=tokens.primitive.gray_300,
        tab_fg=tokens.primitive.gray_700,
        tab_active_bg=tokens.primitive.gray_100,
        tab_active_fg=tokens.primitive.primary_500,
        tab_hover_bg=tokens.primitive.gray_200,
        tab_hover_fg=tokens.primitive.gray_900,

        # Chart/Graph colors
        chart_1=tokens.primitive.primary_500,
        chart_2=tokens.primitive.success_500,
        chart_3=tokens.primitive.warning_500,
        chart_4=tokens.primitive.error_500,
        chart_5="#AB47BC",  # Purple
        chart_6="#26C6DA",  # Cyan
        chart_grid=tokens.primitive.gray_400,
        chart_axis=tokens.primitive.gray_600,
    )

    # Configure typography for dark theme
    tokens.typography = Typography(
        font_family_code="Cascadia Code"  # Modern monospace font
    )

    # Configure syntax highlighting colors for dark theme (VS Code Dark style)
    tokens.syntax = SyntaxColors(
        keyword="#569CD6",  # Light blue
        class_name="#4EC9B0",  # Cyan
        function="#DCDCAA",  # Yellow
        string="#CE9178",  # Orange
        comment="#6A9955",  # Green
        number="#B5CEA8",  # Light green
        operator="#D4D4D4",  # Light gray
        decorator="#DCDCAA",  # Yellow
        constant="#569CD6",  # Light blue
        variable="#9CDCFE",  # Light blue
        parameter="#9CDCFE",  # Light blue
        type="#4EC9B0",  # Cyan
        namespace="#4EC9B0",  # Cyan
        error="#F44747",  # Red
        warning="#FFCC00",  # Yellow
        info="#569CD6",  # Light blue
    )

    return Theme(
        name="dark",
        display_name="Dark",
        description="Modern dark theme for reduced eye strain",
        author="Qt Framework",
        version="2.0.0",
        tokens=tokens,
    )


def create_high_contrast_theme() -> Theme:
    """Create a high contrast theme for accessibility."""
    tokens = DesignTokens()

    # Override primitive colors for high contrast
    tokens.primitive = PrimitiveColors(
        # Pure black and white for maximum contrast
        gray_50="#FFFFFF",
        gray_100="#FFFFFF",
        gray_200="#E0E0E0",
        gray_300="#C0C0C0",
        gray_400="#808080",
        gray_500="#606060",
        gray_600="#404040",
        gray_700="#202020",
        gray_800="#101010",
        gray_900="#000000",
        gray_950="#000000",

        # High contrast primary colors
        primary_50="#E6F3FF",
        primary_100="#CCE7FF",
        primary_200="#99CFFF",
        primary_300="#66B7FF",
        primary_400="#339FFF",
        primary_500="#0080FF",
        primary_600="#0066CC",
        primary_700="#004D99",
        primary_800="#003366",
        primary_900="#001A33",
        primary_950="#000D1A",

        # Keep other colors vibrant for visibility
        white="#FFFFFF",
        black="#000000",
        transparent="transparent",
    )

    # Configure semantic colors for high contrast
    tokens.semantic = SemanticColors(
        # Background
        bg_primary=tokens.primitive.white,
        bg_secondary=tokens.primitive.gray_50,
        bg_tertiary=tokens.primitive.gray_100,
        bg_elevated=tokens.primitive.white,
        bg_overlay="rgba(0, 0, 0, 0.8)",

        # Foreground/Text - maximum contrast
        fg_primary=tokens.primitive.black,
        fg_secondary=tokens.primitive.gray_700,
        fg_tertiary=tokens.primitive.gray_600,
        fg_on_accent=tokens.primitive.white,
        fg_on_dark=tokens.primitive.white,
        fg_on_light=tokens.primitive.black,

        # Interactive states
        action_primary=tokens.primitive.primary_500,
        action_primary_hover=tokens.primitive.primary_600,
        action_primary_active=tokens.primitive.primary_700,
        action_secondary=tokens.primitive.gray_700,
        action_secondary_hover=tokens.primitive.gray_800,
        action_secondary_active=tokens.primitive.gray_900,

        # Feedback - high contrast colors
        feedback_success="#008000",
        feedback_warning="#FF8C00",
        feedback_error="#DC143C",
        feedback_info="#1E90FF",

        # Borders - strong for visibility
        border_default=tokens.primitive.black,
        border_subtle=tokens.primitive.gray_400,
        border_strong=tokens.primitive.black,
        border_focus=tokens.primitive.primary_500,

        # Special states
        state_hover=tokens.primitive.gray_200,
        state_selected=tokens.primitive.primary_100,
        state_disabled=tokens.primitive.gray_300,
        state_focus=tokens.primitive.primary_100,
    )

    # Component colors with high contrast
    tokens.components = ComponentColors(
        # Button
        button_primary_bg=tokens.primitive.primary_500,
        button_primary_fg=tokens.primitive.white,
        button_primary_border=tokens.primitive.black,
        button_secondary_bg=tokens.primitive.white,
        button_secondary_fg=tokens.primitive.black,
        button_secondary_border=tokens.primitive.black,

        # Input
        input_bg=tokens.primitive.white,
        input_fg=tokens.primitive.black,
        input_border=tokens.primitive.black,
        input_placeholder=tokens.primitive.gray_600,

        # Table
        table_header_bg=tokens.primitive.gray_200,
        table_header_fg=tokens.primitive.black,
        table_row_bg=tokens.primitive.white,
        table_row_bg_alt=tokens.primitive.gray_100,
        table_row_hover=tokens.primitive.gray_200,
        table_row_selected=tokens.primitive.primary_100,
        table_border=tokens.primitive.black,

        # Other components follow similar pattern
        menu_bg=tokens.primitive.white,
        menu_fg=tokens.primitive.black,
        scrollbar_bg=tokens.primitive.gray_200,
        scrollbar_thumb=tokens.primitive.black,
        tab_bg=tokens.primitive.gray_100,
        tab_fg=tokens.primitive.black,
        chart_grid=tokens.primitive.gray_400,
    )

    # Configure typography for high contrast theme
    tokens.typography = Typography(
        font_family_code="Consolas"  # Clear monospace font
    )

    # Configure syntax highlighting colors for high contrast
    tokens.syntax = SyntaxColors(
        keyword="#0000FF",  # Blue
        class_name="#267F99",  # Teal
        function="#795E26",  # Brown
        string="#A31515",  # Red
        comment="#008000",  # Green
        number="#098658",  # Dark green
        operator="#000000",  # Black
        decorator="#AA0000",  # Dark red
        constant="#0000FF",  # Blue
        variable="#001080",  # Dark blue
        parameter="#001080",  # Dark blue
        type="#267F99",  # Teal
        namespace="#267F99",  # Teal
        error="#FF0000",  # Red
        warning="#FFA500",  # Orange
        info="#0000FF",  # Blue
    )

    return Theme(
        name="high_contrast",
        display_name="High Contrast",
        description="High contrast theme for improved accessibility",
        author="Qt Framework",
        version="2.0.0",
        tokens=tokens,
    )


# Export built-in themes
BUILTIN_THEMES = {
    "light": create_light_theme,
    "dark": create_dark_theme,
    "high_contrast": create_high_contrast_theme,
}
