"""对话区域组件"""

import re
import customtkinter as ctk
from ui.i18n import T
from ui.widgets import ToolCallCard


def strip_markdown(text: str) -> str:
    """剥离Markdown标记，保留纯文本"""
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*>\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'---+', '', text)
    return text.strip()


def strip_emoji(text: str) -> str:
    """剥离表情符号和特殊Unicode符号"""
    emoji_ranges = (
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
        "\U0001F680-\U0001F6FF"  # Transport and Map
        "\U0001F700-\U0001F77F"  # Alchemical
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U0000FE00-\U0000FE0F"  # Variation Selectors
        "\U0000200D"             # Zero Width Joiner
        "\U00002600-\U000026FF"  # Misc Symbols
        "\U00002B50-\U00002B55"  # Stars and circles
        "\U0000231A-\U0000231B"  # Watch, hourglass
        "\U000023E9-\U000023F3"  # Various symbols
        "\U000023F8-\U000023FA"  # Various symbols
        "\U000025AA-\U000025AB"  # Squares
        "\U000025B6"             # Play button
        "\U000025C0"             # Reverse button
        "\U000025FB-\U000025FE"  # Squares
        "\U00002614-\U00002615"  # Umbrella, hot beverage
        "\U00002648-\U00002653"  # Zodiac
        "\U0000267F"             # Wheelchair
        "\U00002693"             # Anchor
        "\U000026A1"             # Lightning
        "\U000026AA-\U000026AB"  # Circles
        "\U000026BD-\U000026BE"  # Soccer, baseball
        "\U000026C4-\U000026C5"  # Snowman, sun
        "\U000026CE"             # Ophiuchus
        "\U000026D4"             # No entry
        "\U000026EA"             # Church
        "\U000026F2-\U000026F3"  # Fountain, golf
        "\U000026F5"             # Sailboat
        "\U000026FA"             # Tent
        "\U000026FD"             # Fuel pump
        "\U00002702"             # Scissors
        "\U00002705"             # Check mark
        "\U00002708-\U0000270D"  # Various
        "\U0000270F"             # Pencil
        "\U00002712"             # Black nib
        "\U00002714"             # Check mark
        "\U00002716"             # Multiplication
        "\U0000271D"             # Latin cross
        "\U00002721"             # Star of David
        "\U00002728"             # Sparkles
        "\U00002733-\U00002734"  # Eight spoked asterisk
        "\U00002744"             # Snowflake
        "\U00002747"             # Sparkle
        "\U0000274C-\U0000274E"  # Cross marks
        "\U00002753-\U00002755"  # Question marks
        "\U00002757"             # Exclamation
        "\U00002763-\U00002764"  # Heart exclamation, heart
        "\U00002795-\U00002797"  # Plus, minus, divide
        "\U000027A1"             # Right arrow
        "\U000027B0"             # Curly loop
        "]+"
    )
    return re.sub(emoji_ranges, '', text).strip()


class MessageBubble(ctk.CTkFrame):
    """消息气泡"""

    def __init__(self, master, is_user: bool, theme: dict,
                 on_speak=None, on_copy=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.is_user = is_user
        self.on_speak = on_speak
        self.on_copy = on_copy
        self._raw_text = ""

        bubble_color = theme["user_bubble"] if is_user else theme["ai_bubble"]
        self.configure(fg_color=bubble_color)

        # 文本区域
        self.text_box = ctk.CTkTextbox(
            self, font=ctk.CTkFont(size=14), wrap="word",
            activate_scrollbars=True, height=0,
            fg_color="transparent",
        )
        self.text_box.pack(padx=14, pady=(10, 6), fill="both", expand=True)

        # 底部工具栏
        if not is_user:
            toolbar = ctk.CTkFrame(self, fg_color="transparent")
            toolbar.pack(anchor="w", padx=14, pady=(0, 8))

            self.speaker_btn = ctk.CTkButton(
                toolbar, text=T("speak"), width=50, height=26,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=theme["border"],
                text_color=theme["text_secondary"],
                command=self._on_speak_click,
            )
            self.speaker_btn.pack(side="left", padx=(0, 4))

            self.copy_btn = ctk.CTkButton(
                toolbar, text=T("copy"), width=50, height=26,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=theme["border"],
                text_color=theme["text_secondary"],
                command=self._on_copy_click,
            )
            self.copy_btn.pack(side="left")
        else:
            self.speaker_btn = None
            self.copy_btn = None

        self._theme = theme

    def _on_speak_click(self):
        if self.on_speak:
            self.on_speak(self)

    def _on_copy_click(self):
        try:
            text = self.text_box.get("1.0", "end").strip()
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
                if self.copy_btn:
                    self.copy_btn.configure(text=T("copied"))
                    self.after(1500, lambda: self.copy_btn.configure(text=T("copy")))
        except Exception:
            pass

    def set_text(self, text: str):
        self._raw_text = text
        display_text = strip_markdown(text) if not self.is_user else text
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", display_text)
        self.text_box.configure(state="disabled")
        self.after(10, self._resize)

    def append_text(self, text: str):
        self._raw_text += text
        # 流式追加时直接显示原始文本，完成后再处理Markdown
        self.text_box.configure(state="normal")
        self.text_box.insert("end", text)
        self.text_box.configure(state="disabled")
        self.after(10, self._resize)

    def finalize(self):
        """流式完成后，重新处理Markdown显示"""
        if not self.is_user and self._raw_text:
            display_text = strip_markdown(self._raw_text)
            self.text_box.configure(state="normal")
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", display_text)
            self.text_box.configure(state="disabled")
            self.after(10, self._resize)

    def _resize(self):
        try:
            self.text_box.update_idletasks()
            last_line = self.text_box.index("end-1c")
            lines = int(last_line.split(".")[0])
            h = max(30, min(lines * 22 + 10, 6000))
            self.text_box.configure(height=h)
        except Exception:
            pass

    def set_speaking(self, speaking: bool):
        if self.speaker_btn:
            self.speaker_btn.configure(text=T("stop") if speaking else T("speak"))

    def apply_theme(self, theme: dict):
        self._theme = theme
        bubble_color = theme["user_bubble"] if self.is_user else theme["ai_bubble"]
        self.configure(fg_color=bubble_color)
        self.text_box.configure(text_color=theme["text"])
        if self.speaker_btn:
            self.speaker_btn.configure(
                hover_color=theme["border"],
                text_color=theme["text_secondary"],
            )
        if self.copy_btn:
            self.copy_btn.configure(
                hover_color=theme["border"],
                text_color=theme["text_secondary"],
            )


class ThinkingBubble(ctk.CTkFrame):
    """思考中动画气泡"""

    def __init__(self, master, theme: dict, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.configure(fg_color=theme["ai_bubble"])

        self.label = ctk.CTkLabel(
            self, text=T("thinking"),
            font=ctk.CTkFont(size=14),
            text_color=theme["text_secondary"],
        )
        self.label.pack(padx=14, pady=12)
        self._dots = 0
        self._animate()

    def _animate(self):
        try:
            self._dots = (self._dots + 1) % 4
            self.label.configure(text=T("thinking") + "." * self._dots)
            self.after(400, self._animate)
        except Exception:
            pass

    def apply_theme(self, theme: dict):
        self.configure(fg_color=theme["ai_bubble"])
        self.label.configure(text_color=theme["text_secondary"])


class ChatArea(ctk.CTkScrollableFrame):
    """对话区域"""

    def __init__(self, master, theme: dict, on_speak=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.on_speak = on_speak
        self._bubbles = []

        self.configure(fg_color=theme["bg"])

    def add_user_message(self, text: str) -> MessageBubble:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=6, anchor="e")

        bubble = MessageBubble(wrapper, is_user=True, theme=self.theme)
        bubble.pack(anchor="e", padx=(80, 0))
        bubble.set_text(text)
        self._bubbles.append(bubble)
        self._do_scroll()
        return bubble

    def add_ai_message(self) -> MessageBubble:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=6, anchor="w")

        bubble = MessageBubble(
            wrapper, is_user=False, theme=self.theme,
            on_speak=self.on_speak,
        )
        bubble.pack(anchor="w", padx=(0, 80))
        self._bubbles.append(bubble)
        self._do_scroll()
        return bubble

    def add_thinking(self) -> ThinkingBubble:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=6, anchor="w")

        thinking = ThinkingBubble(wrapper, theme=self.theme)
        thinking.pack(anchor="w", padx=(0, 80))
        self._do_scroll()
        return thinking

    def add_tool_card(self, tool_name: str, params: str) -> ToolCallCard:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=4, anchor="w")

        card = ToolCallCard(
            wrapper, theme=self.theme,
            tool_name=tool_name, params=params,
        )
        card.pack(anchor="w", padx=(0, 80), fill="x")
        self._do_scroll()
        return card

    def add_error(self, text: str):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=6)

        label = ctk.CTkLabel(
            wrapper, text=f"{T('error_prefix')}{text}",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["error"],
            wraplength=500,
        )
        label.pack(padx=20)
        self._do_scroll()

    def _do_scroll(self):
        self.after(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self._parent_canvas.yview_moveto(1.0)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.configure(fg_color=theme["bg"])
        for bubble in self._bubbles:
            bubble.apply_theme(theme)
        # 强制刷新
        self.update_idletasks()

    def clear_all(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._bubbles.clear()
        # 重置滚动位置到顶部
        self.after(50, lambda: self._parent_canvas.yview_moveto(0))
