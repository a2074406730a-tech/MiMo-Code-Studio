"""主窗口"""

import uuid
import json
import customtkinter as ctk
from ui.themes import get_theme
from ui.i18n import T, set_lang, get_lang
from ui.sidebar import Sidebar
from ui.chat_area import ChatArea
from ui.input_bar import InputBar
from ui.settings_panel import SettingsPanel
from config import Config, ConversationStore
from api_client import MiMoClient
from audio_player import AudioPlayer


class App(ctk.CTk):
    """主应用窗口"""

    def __init__(self, config: Config, api: MiMoClient, player: AudioPlayer):
        super().__init__()
        self.config = config
        self.api = api
        self.player = player
        self.conv_store = ConversationStore()

        self._dark = config.get("dark_theme", True)
        self._theme = get_theme(self._dark)
        self._current_conv_id = None
        self._speaking_bubble = None

        set_lang(config.get("language", "zh"))

        ctk.set_appearance_mode("dark" if self._dark else "light")
        self.title("MiMo Code Studio")
        self.geometry(f"{config['window_width']}x{config['window_height']}")
        self.minsize(1000, 700)
        self.configure(fg_color=self._theme["bg"])

        # 居中显示
        self.update_idletasks()
        w, h = config["window_width"], config["window_height"]
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self._load_conversations()

    def _build_ui(self):
        t = self._theme

        # 顶部栏
        self.top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)

        ctk.CTkLabel(
            self.top_bar, text="MiMo Code Studio",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=t["text"],
        ).pack(side="left", padx=20)

        top_right = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        top_right.pack(side="right", padx=16)

        # 工作目录显示
        self.dir_label = ctk.CTkLabel(
            top_right, text="",
            font=ctk.CTkFont(size=12),
            text_color=t["text_secondary"],
        )
        self.dir_label.pack(side="left", padx=(0, 12))
        self._update_dir_label()

        self.theme_btn = ctk.CTkButton(
            top_right, text=T("theme_light") if self._dark else T("theme_dark"),
            width=60, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=t["surface"],
            hover_color=t["surface_hover"],
            text_color=t["text"],
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="left", padx=(0, 8))

        self.lang_btn = ctk.CTkButton(
            top_right, text=T("lang_btn"),
            width=50, height=32,
            font=ctk.CTkFont(size=12),
            fg_color=t["surface"],
            hover_color=t["surface_hover"],
            text_color=t["text"],
            command=self._toggle_lang,
        )
        self.lang_btn.pack(side="left", padx=(0, 8))

        # 主体区域
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # 侧边栏
        self.sidebar = Sidebar(
            body, theme=t,
            on_new_chat=self._new_chat,
            on_select_chat=self._select_chat,
            on_delete_chat=self._delete_chat,
            on_rename_chat=self._rename_chat,
            on_settings=self._open_settings,
        )
        self.sidebar.pack(side="left", fill="y")

        # 右侧内容区
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        # 对话区域
        self.chat_area = ChatArea(
            right, theme=t, on_speak=self._on_speak,
        )
        self.chat_area.pack(fill="both", expand=True)

        # 输入栏
        self.input_bar = InputBar(
            right, theme=t, config=self.config,
            on_send=self._on_send,
        )
        self.input_bar.pack(fill="x")

        # 底部状态栏
        self.status_bar = ctk.CTkFrame(self, height=28, corner_radius=0)
        self.status_bar.pack(fill="x")
        self.status_bar.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar, text=T("ready"),
            font=ctk.CTkFont(size=11),
            text_color=t["text_secondary"],
        )
        self.status_label.pack(side="left", padx=16)

        self.model_label = ctk.CTkLabel(
            self.status_bar, text=f"{T('model_prefix')}{self.config['model']}",
            font=ctk.CTkFont(size=11),
            text_color=t["text_secondary"],
        )
        self.model_label.pack(side="right", padx=16)

        self.token_label = ctk.CTkLabel(
            self.status_bar, text="Token: -",
            font=ctk.CTkFont(size=11),
            text_color=t["text_secondary"],
        )
        self.token_label.pack(side="right", padx=8)

        self._apply_theme()

    def _update_dir_label(self):
        wd = self.config.get("working_dir", "")
        self.dir_label.configure(text=wd if wd else T("no_workdir"))

    def _load_conversations(self):
        for conv in self.conv_store.get_all():
            self.sidebar.add_chat_item(conv["id"], conv.get("title", T("new_chat_title")))

    def _toggle_theme(self):
        self._dark = not self._dark
        self.config["dark_theme"] = self._dark
        self.config.save()
        self._theme = get_theme(self._dark)
        ctk.set_appearance_mode("dark" if self._dark else "light")
        self._apply_theme()

    def _toggle_lang(self):
        new_lang = "en" if get_lang() == "zh" else "zh"
        set_lang(new_lang)
        self.config["language"] = new_lang
        self.config.save()
        self._apply_theme()

    def _apply_theme(self):
        t = self._theme
        self.configure(fg_color=t["bg"])

        # 顶部栏
        self.top_bar.configure(fg_color=t["surface"])
        for widget in self.top_bar.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=t["text"])

        # 状态栏
        self.status_bar.configure(fg_color=t["surface"])

        # 按钮
        self.theme_btn.configure(
            text=T("theme_light") if self._dark else T("theme_dark"),
            fg_color=t["surface"], hover_color=t["surface_hover"],
            text_color=t["text"],
        )
        self.lang_btn.configure(
            text=T("lang_btn"),
            fg_color=t["surface"], hover_color=t["surface_hover"],
            text_color=t["text"],
        )

        # 标签
        self.dir_label.configure(text_color=t["text_secondary"])
        self._update_dir_label()
        self.status_label.configure(text_color=t["text_secondary"], text=T("ready"))
        self.model_label.configure(text_color=t["text_secondary"], text=f"{T('model_prefix')}{self.config['model']}")
        self.token_label.configure(text_color=t["text_secondary"])

        # 子组件
        self.sidebar.apply_theme(t)
        self.chat_area.apply_theme(t)
        self.input_bar.apply_theme(t)

        # 强制刷新
        self.update_idletasks()

    def _open_settings(self):
        SettingsPanel(self, self.config, self._theme)

    # 对话管理
    def _new_chat(self):
        conv_id = str(uuid.uuid4())
        self._current_conv_id = conv_id
        self.api.clear_history()
        self.chat_area.clear_all()

        conv = {
            "id": conv_id,
            "title": T("new_chat_title"),
            "messages": [],
        }
        self.conv_store.add(conv)
        self.sidebar.add_chat_item(conv_id, T("new_chat_title"))
        self.sidebar.highlight_chat(conv_id)
        self.input_bar.set_enabled(True)

    def _select_chat(self, conv_id: str):
        self._current_conv_id = conv_id
        conv = self.conv_store.get_by_id(conv_id)
        if not conv:
            return

        self.api.clear_history()
        self.chat_area.clear_all()
        self.input_bar.set_enabled(True)
        self.status_label.configure(text=T("ready"))

        for msg in conv.get("messages", []):
            if msg["role"] == "user":
                self.chat_area.add_user_message(msg["content"])
                self.api.messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                bubble = self.chat_area.add_ai_message()
                if isinstance(msg["content"], str):
                    bubble.set_text(msg["content"])
                elif isinstance(msg["content"], list):
                    # 处理包含tool_use的复杂消息
                    text_parts = [p.get("text", "") for p in msg["content"] if p.get("type") == "text"]
                    bubble.set_text("".join(text_parts))
                self.api.messages.append({"role": "assistant", "content": msg["content"]})

    def _delete_chat(self, conv_id: str):
        self.conv_store.delete(conv_id)
        self.sidebar.remove_chat_item(conv_id)
        if self._current_conv_id == conv_id:
            self._current_conv_id = None
            self.chat_area.clear_all()
            self.api.clear_history()

    def _rename_chat(self, conv_id: str):
        dialog = ctk.CTkInputDialog(
            text=T("rename_prompt"), title=T("rename_title"),
        )
        new_name = dialog.get_input()
        if new_name:
            self.conv_store.update(conv_id, {"title": new_name})
            # 刷新侧边栏显示
            self.sidebar.remove_chat_item(conv_id)
            self.sidebar.add_chat_item(conv_id, new_name)
            if self._current_conv_id == conv_id:
                self.sidebar.highlight_chat(conv_id)

    def _save_message(self, role: str, content):
        if not self._current_conv_id:
            return
        conv = self.conv_store.get_by_id(self._current_conv_id)
        if conv:
            messages = conv.get("messages", [])
            messages.append({"role": role, "content": content})
            self.conv_store.update(self._current_conv_id, {"messages": messages})
            # 更新标题
            if role == "user" and len(messages) == 1:
                title = content[:20] + ("..." if len(content) > 20 else "")
                self.conv_store.update(self._current_conv_id, {"title": title})
                self.sidebar.remove_chat_item(self._current_conv_id)
                self.sidebar.add_chat_item(self._current_conv_id, title)
                self.sidebar.highlight_chat(self._current_conv_id)

    # 发送消息
    def _on_send(self, text: str):
        if not self._current_conv_id:
            self._new_chat()

        # 记录发送时的对话ID，防止回复串流
        send_conv_id = self._current_conv_id

        self.chat_area.add_user_message(text)
        self._save_message("user", text)
        self.input_bar.set_enabled(False)
        self.status_label.configure(text=T("thinking_status"))

        thinking = self.chat_area.add_thinking()
        ai_bubble = None
        tool_cards = []
        thinking_destroyed = False

        def destroy_thinking():
            nonlocal thinking_destroyed
            if not thinking_destroyed:
                try:
                    thinking.destroy()
                except Exception:
                    pass
                thinking_destroyed = True

        def on_token(token):
            nonlocal ai_bubble
            def _update():
                nonlocal ai_bubble
                # 检查是否还在同一个对话
                if self._current_conv_id != send_conv_id:
                    return
                if ai_bubble is None:
                    destroy_thinking()
                    ai_bubble = self.chat_area.add_ai_message()
                ai_bubble.append_text(token)
            self.chat_area.after(0, _update)

        def on_tool_start(name, params):
            def _update():
                if self._current_conv_id != send_conv_id:
                    return
                param_str = json.dumps(params, ensure_ascii=False, indent=2)
                card = self.chat_area.add_tool_card(name, param_str)
                tool_cards.append((name, card))
                self.status_label.configure(text=f"{T('executing_status')}{name}...")
            self.chat_area.after(0, _update)

        def on_tool_result(name, result):
            def _update():
                if self._current_conv_id != send_conv_id:
                    return
                if tool_cards and tool_cards[-1][0] == name:
                    _, card = tool_cards[-1]
                    card.set_result(result[:2000], success=not result.startswith("错误"))
                self.status_label.configure(text=T("thinking_status"))
            self.chat_area.after(0, _update)

        def on_done(full_text):
            def _finish():
                nonlocal ai_bubble
                destroy_thinking()
                # 检查是否还在同一个对话
                if self._current_conv_id != send_conv_id:
                    # 对话已切换，保存消息到原对话，但恢复输入栏
                    conv = self.conv_store.get_by_id(send_conv_id)
                    if conv and full_text:
                        messages = conv.get("messages", [])
                        messages.append({"role": "assistant", "content": full_text})
                        self.conv_store.update(send_conv_id, {"messages": messages})
                    self.input_bar.set_enabled(True)
                    self.status_label.configure(text=T("ready"))
                    return
                if ai_bubble is None:
                    ai_bubble = self.chat_area.add_ai_message()
                    ai_bubble.set_text(full_text)
                else:
                    ai_bubble.finalize()
                self._save_message("assistant", full_text)
                self.input_bar.set_enabled(True)
                self.status_label.configure(text=T("ready"))

                # 累加Token用量
                self.api.total_usage["input_tokens"] += self.api.last_usage.get("input_tokens", 0)
                self.api.total_usage["output_tokens"] += self.api.last_usage.get("output_tokens", 0)
                input_t = self.api.total_usage["input_tokens"]
                output_t = self.api.total_usage["output_tokens"]
                self.token_label.configure(text=f"Token: 输入 {input_t} | 输出 {output_t} | 总计 {input_t + output_t}")

                # 自动朗读
                if self.input_bar.auto_read_var.get() and full_text:
                    self._speak_bubble(ai_bubble)
            self.chat_area.after(0, _finish)

        def on_error(err):
            def _err():
                destroy_thinking()
                if self._current_conv_id != send_conv_id:
                    self.input_bar.set_enabled(True)
                    self.status_label.configure(text=T("ready"))
                    return
                self.chat_area.add_error(err)
                self.input_bar.set_enabled(True)
                self.status_label.configure(text=T("error_status"))
            self.chat_area.after(0, _err)

        self.api.send_message(text, callbacks={
            "on_token": on_token,
            "on_tool_start": on_tool_start,
            "on_tool_result": on_tool_result,
            "on_done": on_done,
            "on_error": on_error,
        })

    # 语音
    def _on_speak(self, bubble):
        if self.player.is_playing and self._speaking_bubble == bubble:
            self.player.stop()
            bubble.set_speaking(False)
            self._speaking_bubble = None
            return
        self._speak_bubble(bubble)

    def _speak_bubble(self, bubble):
        if self._speaking_bubble:
            self._speaking_bubble.set_speaking(False)
        self.player.stop()
        bubble.set_speaking(True)
        self._speaking_bubble = bubble

        # 使用原始文本并剥离Markdown标记和表情符号
        from ui.chat_area import strip_markdown, strip_emoji
        raw_text = getattr(bubble, '_raw_text', '')
        if not raw_text:
            raw_text = bubble.text_box.get("1.0", "end").strip()
        text = strip_emoji(strip_markdown(raw_text))
        if not text:
            bubble.set_speaking(False)
            self._speaking_bubble = None
            return

        def on_end():
            self.after(0, lambda: (
                bubble.set_speaking(False),
                setattr(self, "_speaking_bubble", None),
            ))

        self.player.speak(
            text=text,
            voice=self.input_bar.get_voice_id(),
            rate=self.input_bar.rate_var.get(),
            volume=self.input_bar.volume_var.get(),
            on_end=on_end,
        )

    def destroy(self):
        # 保存窗口大小
        self.config["window_width"] = self.winfo_width()
        self.config["window_height"] = self.winfo_height()
        self.config.save()
        super().destroy()
