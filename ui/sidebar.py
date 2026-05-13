"""侧边栏组件"""

import os
import sys
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
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
        self._file_tree_expanded = False
        self._working_dir = ""

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

        # 文件树区域（可折叠）
        self._build_file_tree()
        self._file_tree_container.pack(fill="x", pady=(0, 4))

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

    # ── 文件树常量 ──────────────────────────────────────
    _SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv',
                  '.idea', '.vscode', '.mypy_cache', '.tox', 'dist', 'build'}
    _DUMMY = "__dummy__"

    def _build_file_tree(self):
        """构建文件树区域"""
        t = self.theme

        # 文件树容器（默认隐藏）
        self._file_tree_container = ctk.CTkFrame(self, fg_color="transparent")

        # 折叠头
        header = ctk.CTkFrame(self._file_tree_container, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(4, 0))

        self._file_tree_toggle = ctk.CTkButton(
            header, text=f"  {T('file_tree')} ▸", height=28,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=t["surface_hover"],
            text_color=t["text_secondary"],
            anchor="w",
            command=self._toggle_file_tree,
        )
        self._file_tree_toggle.pack(fill="x")

        # 树视图容器（默认隐藏）
        self._file_tree_body = ctk.CTkFrame(
            self._file_tree_container, fg_color=t["surface"],
            corner_radius=8,
        )

        # ttk.Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("FileTree.Treeview",
                         background=t["surface"],
                         foreground=t["text"],
                         fieldbackground=t["surface"],
                         borderwidth=0,
                         font=("Segoe UI", 11),
                         rowheight=24)
        style.configure("FileTree.Treeview.Heading",
                         background=t["surface"],
                         foreground=t["text"],
                         font=("Segoe UI", 11))
        style.map("FileTree.Treeview",
                   background=[("selected", t["accent_dim"])],
                   foreground=[("selected", t["text"])])

        self._tree = ttk.Treeview(
            self._file_tree_body,
            style="FileTree.Treeview",
            show="tree",
            selectmode="browse",
        )
        self._tree.pack(fill="both", expand=True, padx=4, pady=4)

        # 绑定展开事件（懒加载子目录）
        self._tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        # 绑定右键菜单
        self._tree.bind("<Button-3>", self._on_tree_right_click)

        # 空提示
        self._file_tree_empty = ctk.CTkLabel(
            self._file_tree_body,
            text=T("file_tree_empty"),
            font=ctk.CTkFont(size=11),
            text_color=t["text_secondary"],
        )

        # 文件树右键菜单引用
        self._file_context_menu = None

    def _toggle_file_tree(self):
        """切换文件树展开/折叠"""
        if self._file_tree_expanded:
            self._file_tree_body.pack_forget()
            self._file_tree_toggle.configure(text=f"  {T('file_tree')} ▸")
            self._file_tree_expanded = False
        else:
            self._file_tree_body.pack(fill="x", padx=8, pady=(0, 4))
            self._file_tree_toggle.configure(text=f"  {T('file_tree')} ▾")
            self._file_tree_expanded = True
            self._refresh_file_tree()

    def _refresh_file_tree(self):
        """刷新文件树内容"""
        for item in self._tree.get_children():
            self._tree.delete(item)

        wd = self._working_dir
        if not wd or not os.path.isdir(wd):
            self._file_tree_empty.pack(padx=8, pady=12)
            return

        self._file_tree_empty.pack_forget()
        self._load_children("", wd)

    def _load_children(self, parent_node: str, dir_path: str):
        """加载目录内容到指定父节点"""
        try:
            entries = sorted(os.listdir(dir_path),
                             key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
        except OSError:
            return

        for name in entries:
            if name.startswith('.'):
                continue
            full_path = os.path.join(dir_path, name)
            is_dir = os.path.isdir(full_path)
            if is_dir and name in self._SKIP_DIRS:
                continue

            icon = "📁 " if is_dir else "📄 "
            node = self._tree.insert(parent_node, "end",
                                      text=f"{icon}{name}",
                                      tags=(full_path,),
                                      open=False)
            if is_dir:
                # 插入占位子节点，让文件夹显示展开箭头
                self._tree.insert(node, "end", text="", tags=(self._DUMMY,))

    def _on_tree_open(self, event=None):
        """展开文件夹时懒加载子内容"""
        node = self._tree.focus()
        if not node:
            return

        tags = self._tree.item(node, "tags")
        if not tags:
            return

        full_path = tags[0]
        if full_path == self._DUMMY:
            return

        # 检查是否只有占位子节点（需要加载真实内容）
        children = self._tree.get_children(node)
        if len(children) == 1:
            child_tags = self._tree.item(children[0], "tags")
            if child_tags and child_tags[0] == self._DUMMY:
                self._tree.delete(children[0])
                self._load_children(node, full_path)

    def _on_tree_right_click(self, event):
        """文件树右键菜单"""
        # 关闭已有菜单
        self._close_file_menu()

        item = self._tree.identify_row(event.y)
        if not item:
            return

        self._tree.selection_set(item)
        tags = self._tree.item(item, "tags")
        if not tags or tags[0] == self._DUMMY:
            return

        full_path = tags[0]
        is_dir = os.path.isdir(full_path)
        name = os.path.basename(full_path)

        t = self.theme
        menu = ctk.CTkToplevel(self)
        menu.geometry(f"+{event.x_root}+{event.y_root}")
        menu.overrideredirect(True)
        menu.configure(fg_color=t["surface"])
        self._file_context_menu = menu

        # 打开按钮
        open_btn = ctk.CTkButton(
            menu, text=f"  {T('file_open')}  ", width=140, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=t["surface_hover"],
            text_color=t["text"],
            anchor="w",
            command=lambda: (menu.destroy(), self._open_file(full_path)),
        )
        open_btn.pack(fill="x", padx=4, pady=(4, 2))

        # 删除警告
        warning_label = ctk.CTkLabel(
            menu, text=T("delete_warning"),
            font=ctk.CTkFont(size=10),
            text_color=t["error"],
            anchor="w",
        )
        warning_label.pack(fill="x", padx=8, pady=(0, 0))

        # 删除按钮（红色）
        delete_btn = ctk.CTkButton(
            menu, text=f"  {T('file_delete')}  ", width=140, height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=t["surface_hover"],
            text_color=t["error"],
            anchor="w",
            command=lambda: (menu.destroy(), self._delete_file(full_path, item)),
        )
        delete_btn.pack(fill="x", padx=4, pady=(0, 4))

        # 点击其他地方关闭
        menu.focus_set()

        def _delayed_bind():
            try:
                menu.bind("<FocusOut>", lambda e: self._close_file_menu())
            except Exception:
                pass
        self.after(150, _delayed_bind)

    def _close_file_menu(self):
        if self._file_context_menu:
            try:
                self._file_context_menu.destroy()
            except Exception:
                pass
            self._file_context_menu = None

    def _open_file(self, path: str):
        """用系统默认程序打开文件/文件夹"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    def _delete_file(self, path: str, tree_node: str):
        """删除文件/文件夹（二次确认）"""
        is_dir = os.path.isdir(path)
        name = os.path.basename(path)

        # 弹出确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title(T("file_delete_confirm_title"))
        dialog.geometry("340x160")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color=self.theme["bg"])

        ctk.CTkLabel(
            dialog, text=name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"],
        ).pack(pady=(20, 4))

        hint = T("file_delete_confirm")
        if is_dir:
            hint = f"📁 {hint}"
        ctk.CTkLabel(
            dialog, text=hint,
            font=ctk.CTkFont(size=12),
            text_color=self.theme["error"],
        ).pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(pady=(0, 12))

        def confirm():
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self._tree.delete(tree_node)
            except Exception:
                pass
            dialog.destroy()

        ctk.CTkButton(
            btn_row, text=T("file_delete"), width=100, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=self.theme["error"],
            hover_color="#cc4444",
            text_color="#ffffff",
            corner_radius=6,
            command=confirm,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text=T("close"), width=100, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=self.theme["surface"],
            hover_color=self.theme["surface_hover"],
            text_color=self.theme["text"],
            corner_radius=6,
            command=dialog.destroy,
        ).pack(side="left", padx=8)

    def set_working_dir(self, path: str):
        """设置工作目录，自动展开文件树"""
        self._working_dir = path
        if path:
            # 自动展开文件树
            if not self._file_tree_expanded:
                self._file_tree_body.pack(fill="x", padx=8, pady=(0, 4))
                self._file_tree_toggle.configure(text=f"  {T('file_tree')} ▾")
                self._file_tree_expanded = True
            self._refresh_file_tree()
        elif self._file_tree_expanded:
            self._refresh_file_tree()

    def refresh_file_tree(self):
        """外部调用：仅在文件树已展开时刷新"""
        if self._file_tree_expanded and self._working_dir:
            self._refresh_file_tree()

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
        self.configure(fg_color=theme["sidebar_bg"])

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

        # 文件树
        self._file_tree_toggle.configure(
            text=f"  {T('file_tree')} {'▾' if self._file_tree_expanded else '▸'}",
            hover_color=theme["surface_hover"],
            text_color=theme["text_secondary"],
        )
        self._file_tree_body.configure(fg_color=theme["surface"])
        style = ttk.Style()
        style.configure("FileTree.Treeview",
                         background=theme["surface"],
                         foreground=theme["text"],
                         fieldbackground=theme["surface"],
                         font=("Segoe UI", 11),
                         rowheight=24)
        style.map("FileTree.Treeview",
                   background=[("selected", theme["accent_dim"])],
                   foreground=[("selected", theme["text"])])
        self._file_tree_empty.configure(text_color=theme["text_secondary"])

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
