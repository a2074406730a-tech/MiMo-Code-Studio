"""自定义组件"""

import customtkinter as ctk
from ui.i18n import T


class IconButton(ctk.CTkButton):
    """图标按钮"""

    def __init__(self, master, icon_text: str, size: int = 36, **kwargs):
        super().__init__(
            master,
            text=icon_text,
            width=size,
            height=size,
            font=ctk.CTkFont(size=int(size * 0.5)),
            corner_radius=8,
            **kwargs,
        )


class AccentButton(ctk.CTkButton):
    """主色调按钮"""

    def __init__(self, master, theme: dict, **kwargs):
        super().__init__(
            master,
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=36,
            corner_radius=8,
            **kwargs,
        )


class LabeledEntry(ctk.CTkFrame):
    """带标签的输入框"""

    def __init__(self, master, label: str, default: str = "",
                 show: str = None, theme: dict = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme or {}

        self.label = ctk.CTkLabel(
            self, text=label,
            font=ctk.CTkFont(size=13),
            text_color=self.theme.get("text_secondary", "#888"),
        )
        self.label.pack(anchor="w", pady=(8, 2))

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x")

        self.entry = ctk.CTkEntry(
            entry_frame, show=show,
            font=ctk.CTkFont(size=13),
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, default)

        self._show = show
        self._visible = False
        if show:
            self.toggle_btn = ctk.CTkButton(
                entry_frame, text=T("show"), width=50, height=28,
                font=ctk.CTkFont(size=11),
                command=self._toggle_visibility,
            )
            self.toggle_btn.pack(side="right", padx=(4, 0))
        else:
            self.toggle_btn = None

    def _toggle_visibility(self):
        self._visible = not self._visible
        self.entry.configure(show="" if self._visible else self._show)
        if self.toggle_btn:
            self.toggle_btn.configure(text=T("hide") if self._visible else T("show"))

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.label.configure(text_color=theme.get("text_secondary", "#888"))
        self.entry.configure(
            fg_color=theme.get("input_bg", "#1e1e2e"),
            text_color=theme.get("text", "#f0ece4"),
            border_color=theme.get("border", "#2a2a2a"),
        )


class ToolCallCard(ctk.CTkFrame):
    """工具调用卡片 — 默认折叠，点击展开"""

    def __init__(self, master, theme: dict, tool_name: str, params: str, **kwargs):
        super().__init__(master, corner_radius=8, **kwargs)
        self.theme = theme
        self._tool_name = tool_name
        self._params = params
        self._result = ""
        self._success = None
        self._expanded = False

        self.configure(fg_color=theme["surface"], border_width=1, border_color=theme["border"])

        # 可点击的摘要行
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        self.summary_frame.pack(fill="x", padx=10, pady=(6, 6))

        self.status_icon = ctk.CTkLabel(
            self.summary_frame, text="⏳",
            font=ctk.CTkFont(size=13),
            text_color=theme["accent"],
        )
        self.status_icon.pack(side="left")

        self.name_label = ctk.CTkLabel(
            self.summary_frame, text=tool_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme["text"],
        )
        self.name_label.pack(side="left", padx=(6, 0))

        self.expand_hint = ctk.CTkLabel(
            self.summary_frame, text="▸",
            font=ctk.CTkFont(size=12),
            text_color=theme["text_secondary"],
        )
        self.expand_hint.pack(side="right")

        # 详情区域（默认隐藏）
        self._detail_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.detail_label = ctk.CTkLabel(
            self._detail_frame, text=params,
            font=ctk.CTkFont(size=11),
            text_color=theme["text_secondary"],
            wraplength=600,
            justify="left",
        )
        self.detail_label.pack(anchor="w", padx=10, pady=(0, 4))

        self.result_box = ctk.CTkTextbox(
            self._detail_frame, font=ctk.CTkFont(family="Consolas", size=11),
            height=0, wrap="word",
        )
        self.result_box.pack(fill="x", padx=10, pady=(0, 8))
        self.result_box.configure(state="disabled")

        # 绑定点击事件
        for widget in [self.summary_frame, self.status_icon, self.name_label, self.expand_hint]:
            widget.bind("<Button-1>", self._toggle)

    def _toggle(self, event=None):
        if self._expanded:
            self._detail_frame.pack_forget()
            self.expand_hint.configure(text="▸")
            self._expanded = False
        else:
            self._detail_frame.pack(fill="x", after=self.summary_frame)
            self.expand_hint.configure(text="▾")
            self._expanded = True

    def set_result(self, result: str, success: bool = True):
        self._result = result
        self._success = success
        icon = "✓" if success else "✗"
        color = self.theme["success"] if success else self.theme["error"]
        self.status_icon.configure(text=icon, text_color=color)
        self.result_box.configure(state="normal")
        self.result_box.insert("1.0", result)
        self.result_box.configure(state="disabled")
        lines = min(result.count("\n") + 1, 15)
        self.result_box.configure(height=lines * 18 + 10)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.configure(fg_color=theme["surface"], border_color=theme["border"])
        self.name_label.configure(text_color=theme["text"])
        self.detail_label.configure(text_color=theme["text_secondary"])


class CursorLabel(ctk.CTkLabel):
    """带闪烁光标的标签"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._cursor_visible = True
        self._animate()

    def _animate(self):
        try:
            self._cursor_visible = not self._cursor_visible
            text = self.cget("text")
            if text.endswith("|"):
                text = text[:-1]
            if self._cursor_visible:
                self.configure(text=text + "|")
            else:
                self.configure(text=text + " ")
            self.after(500, self._animate)
        except Exception:
            pass
