"""主题配色定义"""

DARK_THEME = {
    "bg": "#0a0a0a",
    "surface": "#141414",
    "surface_hover": "#1e1e1e",
    "input_bg": "#1a1a1a",
    "accent": "#d4a843",
    "accent_hover": "#e6bc5a",
    "accent_dim": "#8b7330",
    "user_bubble": "#2a2215",
    "ai_bubble": "#141414",
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
    "bg": "#f5f5f0",
    "surface": "#fafaf5",
    "surface_hover": "#f0efe8",
    "input_bg": "#f8f8f4",
    "accent": "#daa520",
    "accent_hover": "#c8941a",
    "accent_dim": "#e8c860",
    "user_bubble": "#fff5e0",
    "ai_bubble": "#f5f5f0",
    "text": "#1a1a1a",
    "text_secondary": "#777777",
    "border": "#e0ddd4",
    "error": "#d32f2f",
    "success": "#2e7d32",
    "scrollbar": "#cccccc",
    "code_bg": "#eeeecd",
    "sidebar_bg": "#f0efe8",
}


def get_theme(dark: bool = True) -> dict:
    return DARK_THEME if dark else LIGHT_THEME
