"""主题配色定义"""

DARK_THEME = {
    "bg": "#0a0a0a",
    "surface": "#161616",
    "surface_hover": "#1e1e1e",
    "input_bg": "#1a1a1a",
    "accent": "#6ea8fe",
    "accent_hover": "#8dbdff",
    "user_bubble": "#1a2a3a",
    "ai_bubble": "#161616",
    "text": "#e8e8e8",
    "text_secondary": "#888888",
    "border": "#2a2a2a",
    "error": "#ff6b6b",
    "success": "#51cf66",
    "scrollbar": "#333333",
    "code_bg": "#0d0d0d",
    "sidebar_bg": "#111111",
}

LIGHT_THEME = {
    "bg": "#fafaf8",
    "surface": "#ffffff",
    "surface_hover": "#f5f5f5",
    "input_bg": "#f8f8f6",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "user_bubble": "#e8f0fe",
    "ai_bubble": "#f5f5f5",
    "text": "#1a1a1a",
    "text_secondary": "#666666",
    "border": "#e0e0e0",
    "error": "#d32f2f",
    "success": "#2e7d32",
    "scrollbar": "#cccccc",
    "code_bg": "#f0f0f0",
    "sidebar_bg": "#f8f8f8",
}


def get_theme(dark: bool = True) -> dict:
    return DARK_THEME if dark else LIGHT_THEME
