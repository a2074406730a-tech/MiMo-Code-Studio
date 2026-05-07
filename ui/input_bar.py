"""底部输入栏组件"""

import customtkinter as ctk
from ui.i18n import T
from tts_engine import VOICE_LIST


class InputBar(ctk.CTkFrame):
    """底部输入栏"""

    def __init__(self, master, theme: dict, config, on_send=None, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.theme = theme
        self.config = config
        self.on_send = on_send
        self._enabled = True

        self.configure(fg_color=theme["surface"])

        # 输入行
        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(fill="x", padx=16, pady=(12, 6))

        self.text_input = ctk.CTkTextbox(
            input_row, font=ctk.CTkFont(size=14),
            height=36, wrap="word",
        )
        self.text_input.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.text_input.bind("<Return>", self._on_enter)
        self.text_input.bind("<Shift-Return>", lambda e: None)

        self.send_btn = ctk.CTkButton(
            input_row, text=T("send"), width=60, height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
            corner_radius=8,
            command=self._send,
        )
        self.send_btn.pack(side="right")

        # 语音控制行
        voice_row = ctk.CTkFrame(self, fg_color="transparent")
        voice_row.pack(fill="x", padx=16, pady=(0, 10))

        self.voice_var = ctk.StringVar(value=config.get("voice", VOICE_LIST[0][0]))
        self.voice_menu = ctk.CTkOptionMenu(
            voice_row, variable=self.voice_var,
            values=[v[1] for v in VOICE_LIST],
            width=180, height=28, font=ctk.CTkFont(size=12),
        )
        self.voice_menu.pack(side="left", padx=(0, 12))

        # 设置当前语音名称
        for v in VOICE_LIST:
            if v[0] == self.voice_var.get():
                self.voice_menu.set(v[1])
                break

        ctk.CTkLabel(voice_row, text=T("speed"), font=ctk.CTkFont(size=12),
                     text_color=theme["text_secondary"]).pack(side="left", padx=(0, 4))
        self.rate_var = ctk.IntVar(value=config.get("rate", 0))
        self.rate_slider = ctk.CTkSlider(
            voice_row, from_=-50, to=50, variable=self.rate_var,
            width=100, height=16,
        )
        self.rate_slider.pack(side="left", padx=(0, 4))
        self.rate_label = ctk.CTkLabel(
            voice_row, text="0%", font=ctk.CTkFont(size=11), width=36,
            text_color=theme["text_secondary"],
        )
        self.rate_label.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(voice_row, text=T("volume"), font=ctk.CTkFont(size=12),
                     text_color=theme["text_secondary"]).pack(side="left", padx=(0, 4))
        self.volume_var = ctk.IntVar(value=config.get("volume", 80))
        self.volume_slider = ctk.CTkSlider(
            voice_row, from_=0, to=100, variable=self.volume_var,
            width=100, height=16,
        )
        self.volume_slider.pack(side="left", padx=(0, 4))
        self.volume_label = ctk.CTkLabel(
            voice_row, text="80%", font=ctk.CTkFont(size=11), width=36,
            text_color=theme["text_secondary"],
        )
        self.volume_label.pack(side="left", padx=(0, 12))

        # 自动朗读开关
        self.auto_read_var = ctk.BooleanVar(value=config.get("auto_read", False))
        self.auto_read_switch = ctk.CTkSwitch(
            voice_row, text=T("auto_read"), variable=self.auto_read_var,
            font=ctk.CTkFont(size=12),
            text_color=theme["text_secondary"],
            button_color=theme["accent"],
            command=self._on_auto_read_toggle,
        )
        self.auto_read_switch.pack(side="left")

        # 绑定滑块更新
        self.rate_var.trace_add("write", self._update_rate_label)
        self.volume_var.trace_add("write", self._update_volume_label)

    def _update_rate_label(self, *args):
        self.rate_label.configure(text=f"{self.rate_var.get()}%")

    def _update_volume_label(self, *args):
        self.volume_label.configure(text=f"{self.volume_var.get()}%")

    def _on_auto_read_toggle(self):
        self.config["auto_read"] = self.auto_read_var.get()
        self.config.save()

    def _on_enter(self, event):
        if not event.state & 0x1:  # 非Shift
            self._send()
            return "break"

    def _send(self):
        if not self._enabled:
            return
        text = self.text_input.get("1.0", "end").strip()
        if text and self.on_send:
            self.text_input.delete("1.0", "end")
            self.on_send(text)

    def get_voice_id(self) -> str:
        name = self.voice_menu.get()
        for v in VOICE_LIST:
            if v[1] == name:
                return v[0]
        return VOICE_LIST[0][0]

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        state = "normal" if enabled else "disabled"
        self.text_input.configure(state=state)
        if not enabled:
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", T("thinking_placeholder"))
        self.send_btn.configure(state=state)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.configure(fg_color=theme["surface"])
        self.text_input.configure(
            fg_color=theme["input_bg"], text_color=theme["text"],
            border_color=theme["border"],
        )
        self.send_btn.configure(
            text=T("send"),
            fg_color=theme["accent"], hover_color=theme["accent_hover"],
        )
        self.voice_menu.configure(
            fg_color=theme["input_bg"], button_color=theme["border"],
            button_hover_color=theme["scrollbar"],
            text_color=theme["text"],
        )
        for slider in (self.rate_slider, self.volume_slider):
            slider.configure(
                fg_color=theme["border"], progress_color=theme["accent"],
                button_color=theme["accent"], button_hover_color=theme["accent"],
            )
        for lbl in (self.rate_label, self.volume_label):
            lbl.configure(text_color=theme["text_secondary"])
        self.auto_read_switch.configure(
            text=T("auto_read"),
            text_color=theme["text_secondary"],
            button_color=theme["accent"],
        )
