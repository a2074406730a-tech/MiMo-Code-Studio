"""侧边栏组件"""

import customtkinter as ctk
from ui.i18n import T


class Sidebar(ctk.CTkFrame):
    """侧边栏"""

    def __init__(self, master, theme: dict, on_new_chat=None,
                 on_select_chat=None, on_delete_chat=None,
                 on_rename_chat=None, on_settings=None, **kwargs):
        super().__init__(master, width=240, corner_radius=0, **kwargs)
        self.theme = theme
        self.on_new_chat = on_new_chat
        self.on_select_chat = on_select_chat
        self.on_delete_chat = on_delete_chat
        self.on_rename_chat = on_rename_chat
        self.on_settings = on_settings
        self._current_id = None
        self._items = {}

        self.pack_propagate(False)
        self.configure(fg_color=theme["sidebar_bg"])

        # 新对话按钮
        self.new_chat_btn = ctk.CTkButton(
            self, text=T("new_chat"), height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
            corner_radius=8,
            command=self._on_new_chat,
        )
        self.new_chat_btn.pack(fill="x", padx=12, pady=(16, 8))

        # 历史对话列表
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # 底部设置按钮
        self.settings_btn = ctk.CTkButton(
            self, text=T("settings"), height=36,
            font=ctk.CTkFont(size=13),
            fg_color=theme["surface"],
            hover_color=theme["surface_hover"],
            text_color=theme["text"],
            corner_radius=8,
            command=self._on_settings,
        )
        self.settings_btn.pack(fill="x", padx=12, pady=(8, 16))

        # 右键菜单
        self._context_menu = None

    def _on_new_chat(self):
        if self.on_new_chat:
            self.on_new_chat()

    def _on_settings(self):
        if self.on_settings:
            self.on_settings()

    def add_chat_item(self, conv_id: str, title: str):
        """添加对话项"""
        if conv_id in self._items:
            return

        item = ctk.CTkButton(
            self.list_frame,
            text=title[:20] + ("..." if len(title) > 20 else ""),
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=self.theme["surface_hover"],
            text_color=self.theme["text"],
            anchor="w",
            height=36,
            corner_radius=8,
            command=lambda cid=conv_id: self._select_chat(cid),
        )
        item.pack(fill="x", padx=4, pady=2)
        item.bind("<Button-3>", lambda e, cid=conv_id: self._show_context_menu(e, cid))

        self._items[conv_id] = item

    def remove_chat_item(self, conv_id: str):
        """移除对话项"""
        if conv_id in self._items:
            self._items[conv_id].destroy()
            del self._items[conv_id]

    def highlight_chat(self, conv_id: str):
        """高亮当前对话"""
        if self._current_id and self._current_id in self._items:
            self._items[self._current_id].configure(fg_color="transparent")

        self._current_id = conv_id
        if conv_id in self._items:
            self._items[conv_id].configure(fg_color=self.theme["surface_hover"])

    def _select_chat(self, conv_id: str):
        self.highlight_chat(conv_id)
        if self.on_select_chat:
            self.on_select_chat(conv_id)

    def _show_context_menu(self, event, conv_id: str):
        """显示右键菜单"""
        # 关闭已有菜单
        if self._context_menu:
            try:
                self._context_menu.destroy()
            except Exception:
                pass

        menu = ctk.CTkToplevel(self)
        menu.geometry(f"+{event.x_root}+{event.y_root}")
        menu.overrideredirect(True)
        menu.configure(fg_color=self.theme["surface"])
        self._context_menu = menu

        rename_btn = ctk.CTkButton(
            menu, text=T("rename"), width=140, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=self.theme["surface_hover"],
            text_color=self.theme["text"],
            anchor="w",
            command=lambda: (menu.destroy(), self._rename_chat(conv_id)),
        )
        rename_btn.pack(fill="x", padx=4, pady=2)

        # 红色警告
        warning_label = ctk.CTkLabel(
            menu, text=T("delete_warning"),
            font=ctk.CTkFont(size=10),
            text_color=self.theme["error"],
            anchor="w",
        )
        warning_label.pack(fill="x", padx=8, pady=(0, 0))

        delete_btn = ctk.CTkButton(
            menu, text=T("delete"), width=140, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=self.theme["surface_hover"],
            text_color=self.theme["error"],
            anchor="w",
            command=lambda: (menu.destroy(), self._delete_chat(conv_id)),
        )
        delete_btn.pack(fill="x", padx=4, pady=(0, 4))

        # 点击其他地方关闭菜单
        def close_menu(e=None):
            try:
                menu.destroy()
            except Exception:
                pass
            self._context_menu = None

        menu.focus_set()

        # 延迟绑定，避免立即触发
        def _delayed_bind():
            try:
                menu.bind("<FocusOut>", close_menu)
            except Exception:
                pass
        self.after(150, _delayed_bind)

    def _rename_chat(self, conv_id: str):
        if self.on_rename_chat:
            self.on_rename_chat(conv_id)

    def _delete_chat(self, conv_id: str):
        if self.on_delete_chat:
            self.on_delete_chat(conv_id)

    def apply_theme(self, theme: dict):
        self.theme = theme
        # 使用与主区域一致的背景色
        self.configure(fg_color=theme["surface"])

        # 列表区域
        self.list_frame.configure(fg_color="transparent")

        # 新对话按钮
        self.new_chat_btn.configure(
            text=T("new_chat"),
            fg_color=theme["accent"],
            hover_color=theme["accent_hover"],
            text_color="#000000",
        )

        # 设置按钮
        self.settings_btn.configure(
            text=T("settings"),
            fg_color=theme["input_bg"],
            hover_color=theme["surface_hover"],
            text_color=theme["text"],
        )

        # 历史对话项
        for item in self._items.values():
            item.configure(
                fg_color="transparent",
                hover_color=theme["surface_hover"],
                text_color=theme["text"],
            )

        # 高亮当前对话
        if self._current_id and self._current_id in self._items:
            self._items[self._current_id].configure(fg_color=theme["input_bg"])
