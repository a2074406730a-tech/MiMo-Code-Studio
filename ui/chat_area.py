"""对话区域组件"""

import re
import tkinter as tk
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
        # 强制文字左对齐
        self.text_box._textbox.tag_configure("justify_left", justify="left")
        self.text_box._textbox.tag_add("justify_left", "1.0", "end")

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
            h = max(56, min(lines * 22 + 10, 6000))
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
        self.text_box.configure(fg_color=bubble_color, text_color=theme["text"])
        if self.speaker_btn:
            self.speaker_btn.configure(
                text=T("speak"),
                hover_color=theme["border"],
                text_color=theme["text_secondary"],
            )
        if self.copy_btn:
            self.copy_btn.configure(
                text=T("copy"),
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


class GlowLogo(ctk.CTkFrame):
    """高级发光 Logo — 呼吸灯 + 浮动粒子 + 流光扫过"""

    def __init__(self, master, theme: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = theme
        self._running = True
        self._phase = 0.0
        self.W, self.H = 1040, 280

        # 粒子系统
        import random
        self._particles = []
        for _ in range(44):
            self._particles.append({
                "x": random.uniform(0, self.W),
                "y": random.uniform(0, self.H),
                "vx": random.uniform(-0.8, 0.8),
                "vy": random.uniform(-1.2, -0.2),
                "r": random.uniform(3.6, 8.0),
                "phase": random.uniform(0, 6.28),
            })

        self.canvas = tk.Canvas(
            self, width=self.W, height=self.H,
            highlightthickness=0,
            bg=theme.get("bg", "#0a0a0a"),
        )
        self.canvas.pack(expand=True)
        self._tick()

    # ── 颜色工具 ──────────────────────────────────────
    def _mix(self, c1, c2, t):
        """两色线性插值，t∈[0,1]"""
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{min(255,max(0,r)):02x}{min(255,max(0,g)):02x}{min(255,max(0,b)):02x}"

    def _accent(self, brightness=1.0):
        a = self.theme.get("accent", "#d4a843")
        return self._mix(self.theme.get("bg", "#0a0a0a"), a, brightness)

    # ── 绘制 ──────────────────────────────────────────
    def _render(self):
        self.canvas.delete("all")
        cx, cy = self.W // 2, self.H // 2
        p = self._phase

        import math
        breathe = 0.55 + 0.45 * math.sin(p)
        shimmer_pos = (math.sin(p * 0.7) + 1) / 2

        # ── 1. 背景径向辉光（多层，从外到内）──
        for i in range(8):
            ratio = 0.04 + 0.06 * i
            rx = 480 - i * 36
            ry = 110 - i * 10
            if rx < 40 or ry < 10:
                continue
            self.canvas.create_oval(
                cx - rx, cy - ry, cx + rx, cy + ry,
                fill="", outline=self._accent(ratio * breathe), width=1,
            )

        # ── 2. 左右装饰细线 + 端点菱形 ──
        line_half = int(380 * breathe)
        line_color = self._accent(0.35 * breathe)
        for sx in [-1, 1]:
            x0 = cx + sx * 100
            x1 = cx + sx * line_half
            self.canvas.create_line(x0, cy, x1, cy,
                                    fill=line_color, width=1)
            # 端点菱形
            d = 6
            lx = x1
            self.canvas.create_polygon(
                lx, cy - d, lx + d, cy, lx, cy + d, lx - d, cy,
                fill=self._accent(0.3 * breathe), outline="",
            )

        # ── 3. 精致角标 ──
        bracket_color = self._accent(0.4 * breathe)
        dot_color = self._accent(0.55 * breathe)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            bx = cx + dx * 420
            by = cy + dy * 84
            arm = 20
            self.canvas.create_line(bx, by, bx + dx * arm, by,
                                    fill=bracket_color, width=1)
            self.canvas.create_line(bx, by, bx, by + dy * arm,
                                    fill=bracket_color, width=1)
            self.canvas.create_oval(
                bx - 3, by - 3, bx + 3, by + 3,
                fill=dot_color, outline="",
            )

        # ── 4. 主文字 — 5层发光 ──
        font_spec = ("Segoe UI", 56, "bold")
        # 第1层：最外层大范围柔光
        self.canvas.create_text(
            cx, cy, text="MiMo Code Studio",
            font=font_spec,
            fill=self._accent(0.08 * breathe), anchor="center",
        )
        # 第2层：外层光晕
        self.canvas.create_text(
            cx, cy, text="MiMo Code Studio",
            font=font_spec,
            fill=self._accent(0.2 * breathe), anchor="center",
        )
        # 第3层：中层光晕
        self.canvas.create_text(
            cx, cy, text="MiMo Code Studio",
            font=font_spec,
            fill=self._accent(0.45 * breathe), anchor="center",
        )
        # 第4层：内层明亮
        self.canvas.create_text(
            cx, cy, text="MiMo Code Studio",
            font=font_spec,
            fill=self._accent(0.7 + 0.2 * breathe), anchor="center",
        )
        # 第5层：流光高亮主文字
        shimmer_boost = max(0, 0.4 * (1 - abs(shimmer_pos - 0.5) * 3))
        final_b = min(1.0, 0.8 + 0.2 * breathe + shimmer_boost)
        white_t = shimmer_boost * 0.6
        text_color = self._mix(self._accent(final_b), "#ffffff", white_t)
        self.canvas.create_text(
            cx, cy, text="MiMo Code Studio",
            font=font_spec,
            fill=text_color, anchor="center",
        )

        # ── 5. 下方细线 ──
        rule_half = int(200 * breathe)
        self.canvas.create_line(cx - rule_half, cy + 44, cx + rule_half, cy + 44,
                                fill=self._accent(0.18 * breathe), width=1)

        # ── 6. 浮动粒子（更大更亮）──
        for pt in self._particles:
            flicker = (math.sin(pt["phase"] + p * 3) + 1) / 2
            alpha = 0.25 + 0.45 * flicker
            pr = pt["r"] * (0.7 + 0.3 * breathe)
            if pr < 1.6:
                continue
            color = self._accent(alpha * breathe)
            self.canvas.create_oval(
                pt["x"] - pr, pt["y"] - pr,
                pt["x"] + pr, pt["y"] + pr,
                fill=color, outline="",
            )

    # ── 动画循环 ─────────────────────────────────────
    def _tick(self):
        if not self._running:
            return
        try:
            if not self.winfo_exists():
                return
            self._phase += 0.035
            # 更新粒子位置
            for pt in self._particles:
                pt["x"] += pt["vx"]
                pt["y"] += pt["vy"]
                if pt["y"] < -5:
                    pt["y"] = self.H + 5
                    pt["x"] = __import__("random").uniform(0, self.W)
                if pt["x"] < -5:
                    pt["x"] = self.W + 5
                elif pt["x"] > self.W + 5:
                    pt["x"] = -5
            self._render()
            self.after(40, self._tick)
        except Exception:
            pass

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.canvas.configure(bg=theme.get("bg", "#0a0a0a"))

    def stop(self):
        self._running = False


class ChatArea(ctk.CTkScrollableFrame):
    """对话区域"""

    def __init__(self, master, theme: dict, on_speak=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.on_speak = on_speak
        self._bubbles = []

        self.configure(fg_color=theme["bg"])
        self._scrollbar_visible = True
        self._scrollbar.pack_forget()
        self._scrollbar_visible = False

        # 强制 content frame 跟随 canvas 宽度（CTkScrollableFrame 的关键修复）
        self._parent_canvas.bind("<Configure>", self._on_canvas_resize)

        # 品牌水印（GlowLogo 发光动画）
        self._logo = None
        self._create_watermark()

    def _on_canvas_resize(self, event=None):
        try:
            cw = self._parent_canvas.winfo_width()
            if cw > 1:
                self._parent_canvas.itemconfigure(
                    self._create_window_id, width=cw
                )
            self._center_watermark()
        except Exception:
            pass

    def _create_watermark(self):
        if self._logo:
            return
        # 清理残留canvas项
        try:
            self._parent_canvas.delete("watermark")
        except Exception:
            pass
        self._logo = GlowLogo(self._parent_canvas, theme=self.theme)
        self._parent_canvas.create_window(
            0, 0, window=self._logo, anchor="center",
            tags="watermark",
        )
        self.after(100, self._center_watermark)

    def _center_watermark(self):
        try:
            cw = self._parent_canvas.winfo_width()
            ch = self._parent_canvas.winfo_height()
            self._parent_canvas.coords("watermark", cw // 2, ch // 2)
        except Exception:
            pass

    def _hide_watermark(self):
        if self._logo:
            try:
                self._logo.stop()
            except Exception:
                pass
            try:
                self._parent_canvas.delete("watermark")
            except Exception:
                pass
            try:
                if self._logo.winfo_exists():
                    self._logo.destroy()
            except Exception:
                pass
            self._logo = None

    def _check_scrollbar(self):
        try:
            self.update_idletasks()
            bbox = self._parent_canvas.bbox("all")
            if bbox:
                content_h = bbox[3] - bbox[1]
                view_h = self._parent_canvas.winfo_height()
                need_scroll = content_h > view_h + 10
            else:
                need_scroll = False

            if need_scroll != self._scrollbar_visible:
                self._scrollbar_visible = need_scroll
                if need_scroll:
                    self._scrollbar.pack(side="right", fill="y")
                else:
                    self._scrollbar.pack_forget()
        except Exception:
            pass

    def add_user_message(self, text: str) -> MessageBubble:
        self._hide_watermark()

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=(8, 4))

        bubble = MessageBubble(wrapper, is_user=True, theme=self.theme)
        bubble.pack(anchor="e", padx=(80, 10))
        bubble.set_text(text)
        self._bubbles.append(bubble)
        self._do_scroll()
        return bubble

    def add_ai_message(self) -> MessageBubble:
        self._hide_watermark()

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=(8, 4))

        bubble = MessageBubble(
            wrapper, is_user=False, theme=self.theme,
            on_speak=self.on_speak,
        )
        bubble.pack(anchor="w", padx=(10, 60))
        self._bubbles.append(bubble)
        self._do_scroll()
        return bubble

    def add_thinking(self) -> ThinkingBubble:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=(8, 4))

        thinking = ThinkingBubble(wrapper, theme=self.theme)
        thinking.pack(anchor="w", padx=(10, 60))
        self._do_scroll()
        return thinking

    def add_tool_card(self, tool_name: str, params: str) -> ToolCallCard:
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=4)

        card = ToolCallCard(
            wrapper, theme=self.theme,
            tool_name=tool_name, params=params,
        )
        card.pack(anchor="w", padx=(10, 60), fill="x")
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
        label.pack(anchor="w", padx=20)
        self._do_scroll()

    def add_paused(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=6)

        label = ctk.CTkLabel(
            wrapper, text=f"⏸  {T('paused_status')}",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_secondary"],
        )
        label.pack(anchor="w", padx=20)
        self._do_scroll()

    def _do_scroll(self):
        self.after(50, self._scroll_to_bottom)
        self.after(100, self._check_scrollbar)

    def _scroll_to_bottom(self):
        self._parent_canvas.yview_moveto(1.0)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.configure(fg_color=theme["bg"])
        # 更新logo背景色和主题色
        if self._logo:
            self._logo.apply_theme(theme)
        for bubble in self._bubbles:
            bubble.apply_theme(theme)
        # 更新所有wrapper frame的背景色
        for wrapper in self.winfo_children():
            if isinstance(wrapper, ctk.CTkFrame):
                wrapper.configure(fg_color="transparent")
        # 强制刷新
        self.update_idletasks()

    def clear_all(self):
        # 先清理logo（在canvas上，不在winfo_children里）
        self._hide_watermark()
        for widget in self.winfo_children():
            widget.destroy()
        self._bubbles.clear()
        # 重置滚动位置到顶部
        self.after(50, lambda: self._parent_canvas.yview_moveto(0))
        # 重新显示水印
        self._create_watermark()
        # 隐藏滚动条
        self._scrollbar_visible = False
        try:
            self._scrollbar.pack_forget()
        except Exception:
            pass
