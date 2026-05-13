"""设置面板"""

import os
import customtkinter as ctk
from tkinter import filedialog
from ui.i18n import T


class SettingsPanel(ctk.CTkToplevel):
    """设置面板 - 右侧滑出"""

    def __init__(self, master, config, theme: dict, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.theme = theme
        self._on_save = on_save
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
        # 模型列表管理
        ctk.CTkLabel(
            scroll, text=T("model_name"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme["text"],
        ).pack(anchor="w", pady=(8, 4))

        model_add_row = ctk.CTkFrame(scroll, fg_color="transparent")
        model_add_row.pack(fill="x", pady=(0, 4))

        self.model_name_entry = ctk.CTkEntry(
            model_add_row, font=ctk.CTkFont(size=13),
            placeholder_text=T("model_placeholder"),
        )
        self.model_name_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_model_btn = ctk.CTkButton(
            model_add_row, text=T("add_model"), width=60, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
            command=self._add_model,
        )
        add_model_btn.pack(side="right")

        self.model_tags_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.model_tags_frame.pack(fill="x", pady=(0, 4))
        self._model_tags = []
        self._refresh_model_tags()

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
            self, text=T("credit"),
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

    def _add_model(self):
        name = self.model_name_entry.get().strip()
        if not name:
            return
        models_list = self.config.get("models", [])
        if name not in models_list:
            models_list.append(name)
            self.config.set("models", models_list)
            self.config["model"] = name
            self.model_name_entry.delete(0, "end")
            self._refresh_model_tags()

    def _remove_model(self, name):
        models_list = self.config.get("models", [])
        if name in models_list:
            models_list.remove(name)
            self.config.set("models", models_list)
            if self.config["model"] == name:
                self.config["model"] = models_list[0] if models_list else ""
            self._refresh_model_tags()

    def _refresh_model_tags(self):
        for tag in self._model_tags:
            tag.destroy()
        self._model_tags.clear()

        models_list = self.config.get("models", [self.config.get("model", "mimo-v2.5-pro")])
        current_model = self.config.get("model", "")

        for name in models_list:
            tag = ctk.CTkFrame(self.model_tags_frame, fg_color=self.theme["surface"],
                               corner_radius=6, border_width=1,
                               border_color=self.theme["accent"] if name == current_model else self.theme["border"])
            tag.pack(side="left", padx=(0, 4), pady=2)

            ctk.CTkLabel(
                tag, text=name,
                font=ctk.CTkFont(size=11),
                text_color=self.theme["text"],
            ).pack(side="left", padx=(6, 2), pady=2)

            ctk.CTkButton(
                tag, text="x", width=18, height=18,
                font=ctk.CTkFont(size=10),
                fg_color="transparent",
                hover_color=self.theme["error"],
                text_color=self.theme["text_secondary"],
                command=lambda n=name: self._remove_model(n),
            ).pack(side="right", padx=(0, 4), pady=2)

            self._model_tags.append(tag)

    def _save(self):
        self.config["api_url"] = self.url_entry.get()
        self.config["api_key"] = self.key_entry.get()
        try:
            self.config["max_tokens"] = int(self.tokens_entry.get())
        except ValueError:
            pass
        self.config["system_prompt"] = self.system_prompt_box.get("1.0", "end").strip()
        self.config["working_dir"] = self.working_dir_entry.get()
        self.config.save()
        if hasattr(self, '_on_save') and self._on_save:
            self._on_save()
        self.destroy()
