"""设置面板"""

import os
import customtkinter as ctk
from tkinter import filedialog
from ui.i18n import T


class SettingsPanel(ctk.CTkToplevel):
    """设置面板 - 右侧滑出"""

    def __init__(self, master, config, theme: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.theme = theme
        self.title(T("settings_title"))
        self.geometry("420x600")
        self.resizable(False, False)
        self.grab_set()

        self.configure(fg_color=theme["bg"])

        # 标题
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 16))

        ctk.CTkLabel(
            title_frame, text=T("settings_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme["text"],
        ).pack(side="left")

        close_btn = ctk.CTkButton(
            title_frame, text=T("close"), width=60, height=32,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=theme["surface_hover"],
            text_color=theme["text_secondary"],
            command=self.destroy,
        )
        close_btn.pack(side="right")

        # 滚动区域
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=0)

        # API 配置
        ctk.CTkLabel(
            scroll, text=T("api_config"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w", pady=(8, 8))

        self.url_entry = self._add_field(scroll, T("api_url"), config["api_url"])
        self.key_entry = self._add_field(scroll, T("api_key"), config["api_key"], show="•")
        self.model_entry = self._add_field(scroll, T("model_name"), config["model"])
        self.tokens_entry = self._add_field(scroll, T("max_tokens"), str(config["max_tokens"]))

        # 系统提示词
        ctk.CTkLabel(
            scroll, text=T("system_prompt"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w", pady=(16, 8))

        self.system_prompt_box = ctk.CTkTextbox(
            scroll, font=ctk.CTkFont(size=13),
            height=100, wrap="word",
        )
        self.system_prompt_box.pack(fill="x", pady=(0, 4))
        self.system_prompt_box.insert("1.0", config.get("system_prompt", ""))

        # 工作目录
        ctk.CTkLabel(
            scroll, text=T("working_dir"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w", pady=(16, 8))

        dir_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        dir_frame.pack(fill="x", pady=(0, 4))

        self.working_dir_entry = ctk.CTkEntry(
            dir_frame, font=ctk.CTkFont(size=13),
        )
        self.working_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.working_dir_entry.insert(0, config.get("working_dir", ""))

        browse_btn = ctk.CTkButton(
            dir_frame, text=T("browse"), width=60, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=theme["surface"],
            hover_color=theme["surface_hover"],
            text_color=theme["text"],
            command=self._browse_dir,
        )
        browse_btn.pack(side="right")

        # 保存按钮
        save_btn = ctk.CTkButton(
            self, text=T("save_settings"), height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
            corner_radius=8,
            command=self._save,
        )
        save_btn.pack(fill="x", padx=24, pady=(16, 12))

        # 版权信息
        credit_label = ctk.CTkLabel(
            self, text="wuhenlol 开源制作",
            font=ctk.CTkFont(size=12),
            text_color=theme["text_secondary"],
        )
        credit_label.pack(pady=(0, 16))

    def _add_field(self, parent, label: str, default: str, show: str = None):
        ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text_secondary"],
        ).pack(anchor="w", pady=(8, 2))

        entry = ctk.CTkEntry(parent, show=show, font=ctk.CTkFont(size=13))
        entry.pack(fill="x", pady=(0, 4))
        entry.insert(0, default)

        if show:
            ctk.CTkButton(
                parent, text=T("show"), width=50, height=24,
                font=ctk.CTkFont(size=11),
                fg_color="transparent",
                hover_color=self.theme["surface_hover"],
                text_color=self.theme["text_secondary"],
                command=lambda: self._toggle_visibility(entry, show),
            ).pack(anchor="e")

        return entry

    def _toggle_visibility(self, entry, show_char):
        current_show = entry.cget("show")
        entry.configure(show="" if current_show else show_char)

    def _browse_dir(self):
        current = self.working_dir_entry.get()
        initial_dir = current if current and os.path.isdir(current) else os.path.expanduser("~")
        directory = filedialog.askdirectory(initialdir=initial_dir, title=T("select_workdir"))
        if directory:
            self.working_dir_entry.delete(0, "end")
            self.working_dir_entry.insert(0, directory)

    def _save(self):
        self.config["api_url"] = self.url_entry.get()
        self.config["api_key"] = self.key_entry.get()
        self.config["model"] = self.model_entry.get()
        try:
            self.config["max_tokens"] = int(self.tokens_entry.get())
        except ValueError:
            pass
        self.config["system_prompt"] = self.system_prompt_box.get("1.0", "end").strip()
        self.config["working_dir"] = self.working_dir_entry.get()
        self.config.save()
        self.destroy()
