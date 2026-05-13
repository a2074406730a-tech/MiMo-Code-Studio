"""配置管理模块"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")

DEFAULT_SETTINGS = {
    "api_url": "https://your-api-endpoint/v1/messages",
    "api_key": "",
    "model": "mimo-v2.5-pro",
    "max_tokens": 4096,
    "system_prompt": "你是 MiMo，一个友好的AI助手。你可以进行日常闲聊，也可以帮助用户编写和调试代码。\n\n规则：\n1. 用户只是在聊天、打招呼、问简单问题时，直接用自然语言回答，不要调用任何工具\n2. 只有当用户明确要求读写文件、执行命令、搜索代码等操作时，才使用工具\n3. 不确定是否需要用工具时，优先不用工具，直接回答\n4. 用中文回答",
    "working_dir": "",
    "auto_read": False,
    "dark_theme": True,
    "language": "zh",
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": 0,
    "volume": 80,
    "window_width": 1000,
    "window_height": 700,
    "sidebar_width": 240,
}


class Config:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except Exception:
                pass

    def save(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


class ConversationStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._conversations = []
        self.load()

    def load(self):
        if os.path.exists(CONVERSATIONS_FILE):
            try:
                with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                    self._conversations = json.load(f)
            except Exception:
                self._conversations = []

    def save(self):
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._conversations, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list:
        return self._conversations

    def add(self, conversation: dict):
        self._conversations.insert(0, conversation)
        self.save()

    def update(self, conv_id: str, data: dict):
        for conv in self._conversations:
            if conv.get("id") == conv_id:
                conv.update(data)
                self.save()
                return

    def delete(self, conv_id: str):
        self._conversations = [c for c in self._conversations if c.get("id") != conv_id]
        self.save()

    def get_by_id(self, conv_id: str) -> dict | None:
        for conv in self._conversations:
            if conv.get("id") == conv_id:
                return conv
        return None
