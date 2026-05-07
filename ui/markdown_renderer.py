"""Markdown渲染模块"""

import re
import customtkinter as ctk
from ui.i18n import T
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import RawTokenFormatter


class MarkdownRenderer(ctk.CTkScrollableFrame):
    """Markdown渲染器"""

    def __init__(self, master, theme: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.configure(fg_color="transparent")
        self._widgets = []

    def clear(self):
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()

    def render(self, text: str):
        """渲染Markdown文本"""
        self.clear()
        blocks = self._parse_blocks(text)
        for block in blocks:
            self._render_block(block)

    def append_text(self, text: str):
        """追加文本（流式用）"""
        # 简单实现：重新渲染全部
        # 更复杂的实现可以增量更新
        pass

    def _parse_blocks(self, text: str) -> list:
        """解析Markdown为块"""
        blocks = []
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # 代码块
            if line.strip().startswith("```"):
                lang = line.strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append({"type": "code", "lang": lang, "content": "\n".join(code_lines)})
                i += 1
                continue

            # 标题
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                content = line.lstrip("#").strip()
                blocks.append({"type": "heading", "level": level, "content": content})
                i += 1
                continue

            # 普通文本
            text_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```") and not lines[i].startswith("#"):
                text_lines.append(lines[i])
                i += 1
            blocks.append({"type": "text", "content": "\n".join(text_lines)})

        return blocks

    def _render_block(self, block: dict):
        """渲染单个块"""
        btype = block["type"]

        if btype == "code":
            self._render_code(block["lang"], block["content"])
        elif btype == "heading":
            self._render_heading(block["level"], block["content"])
        else:
            self._render_text(block["content"])

    def _render_code(self, lang: str, code: str):
        """渲染代码块"""
        frame = ctk.CTkFrame(self, corner_radius=8, fg_color=self.theme["code_bg"])
        frame.pack(fill="x", padx=4, pady=4)

        # 顶部栏
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(6, 0))

        lang_label = ctk.CTkLabel(
            header, text=lang or "text",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"],
        )
        lang_label.pack(side="left")

        copy_btn = ctk.CTkButton(
            header, text=T("copy"), width=50, height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=self.theme["surface_hover"],
            text_color=self.theme["text_secondary"],
            command=lambda: self._copy_code(code),
        )
        copy_btn.pack(side="right")

        # 代码内容
        code_box = ctk.CTkTextbox(
            frame, font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word", fg_color="transparent",
        )
        code_box.pack(fill="x", padx=8, pady=(4, 8))

        # 语法高亮
        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()

        # 简单高亮：直接插入代码
        code_box.insert("1.0", code)
        code_box.configure(state="disabled")

        lines = code.count("\n") + 1
        code_box.configure(height=min(lines * 18 + 10, 400))

        self._widgets.append(frame)

    def _render_heading(self, level: int, content: str):
        """渲染标题"""
        sizes = {1: 22, 2: 18, 3: 16, 4: 14, 5: 13, 6: 12}
        size = sizes.get(level, 14)

        label = ctk.CTkLabel(
            self, text=content,
            font=ctk.CTkFont(size=size, weight="bold"),
            text_color=self.theme["text"],
            anchor="w",
            wraplength=700,
        )
        label.pack(fill="x", padx=4, pady=(8, 4))
        self._widgets.append(label)

    def _render_text(self, content: str):
        """渲染普通文本"""
        if not content.strip():
            return

        # 处理内联格式
        lines = content.split("\n")
        for line in lines:
            if not line.strip():
                spacer = ctk.CTkFrame(self, height=4, fg_color="transparent")
                spacer.pack(fill="x")
                self._widgets.append(spacer)
                continue

            label = ctk.CTkLabel(
                self, text=line,
                font=ctk.CTkFont(size=14),
                text_color=self.theme["text"],
                anchor="w",
                wraplength=700,
                justify="left",
            )
            label.pack(fill="x", padx=4, pady=1)
            self._widgets.append(label)

    def _copy_code(self, code: str):
        """复制代码到剪贴板"""
        self.clipboard_clear()
        self.clipboard_append(code)

    def apply_theme(self, theme: dict):
        self.theme = theme
