"""国际化模块 - 中英文切换"""

_current_lang = "zh"

TRANSLATIONS = {
    "zh": {
        # 顶部栏
        "app_title": "MiMo Code Studio",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "lang_btn": "EN",
        "no_workdir": "未设置工作目录",

        # 状态栏
        "ready": "就绪",
        "model_prefix": "模型: ",
        "token_prefix": "Token: ",

        # 侧边栏
        "new_chat": "新对话",
        "settings": "设置",
        "rename": "重命名",
        "delete": "删除",
        "delete_warning": "⚠ 删除后不可恢复",

        # 输入栏
        "send": "发送",
        "speed": "语速",
        "volume": "音量",
        "auto_read": "自动朗读",
        "thinking_placeholder": "MiMo 正在思考...",

        # 对话区域
        "speak": "朗读",
        "copy": "复制",
        "copied": "已复制",
        "stop": "停止",
        "thinking": "思考中",
        "error_prefix": "错误：",

        # 工具卡片
        "executing": "执行中...",
        "completed": "完成",
        "failed": "失败",

        # 设置面板
        "settings_title": "设置",
        "close": "关闭",
        "api_config": "API 配置",
        "api_url": "API 地址",
        "api_key": "API Key",
        "model_name": "模型名称",
        "max_tokens": "Max Tokens",
        "system_prompt": "系统提示词",
        "working_dir": "工作目录",
        "browse": "浏览",
        "save_settings": "保存设置",
        "show": "显示",
        "hide": "隐藏",
        "select_workdir": "选择工作目录",

        # 对话管理
        "rename_title": "重命名对话",
        "rename_prompt": "输入新名称：",
        "new_chat_title": "新对话",

        # 状态
        "thinking_status": "正在思考...",
        "executing_status": "正在执行: ",
        "error_status": "出错了",
    },
    "en": {
        # Top bar
        "app_title": "MiMo Code Studio",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "lang_btn": "中文",
        "no_workdir": "No working directory",

        # Status bar
        "ready": "Ready",
        "model_prefix": "Model: ",
        "token_prefix": "Token: ",

        # Sidebar
        "new_chat": "New Chat",
        "settings": "Settings",
        "rename": "Rename",
        "delete": "Delete",
        "delete_warning": "⚠ Cannot be undone",

        # Input bar
        "send": "Send",
        "speed": "Speed",
        "volume": "Volume",
        "auto_read": "Auto Read",
        "thinking_placeholder": "MiMo is thinking...",

        # Chat area
        "speak": "Speak",
        "copy": "Copy",
        "copied": "Copied",
        "stop": "Stop",
        "thinking": "Thinking",
        "error_prefix": "Error: ",

        # Tool card
        "executing": "Executing...",
        "completed": "Done",
        "failed": "Failed",

        # Settings panel
        "settings_title": "Settings",
        "close": "Close",
        "api_config": "API Configuration",
        "api_url": "API URL",
        "api_key": "API Key",
        "model_name": "Model Name",
        "max_tokens": "Max Tokens",
        "system_prompt": "System Prompt",
        "working_dir": "Working Directory",
        "browse": "Browse",
        "save_settings": "Save Settings",
        "show": "Show",
        "hide": "Hide",
        "select_workdir": "Select Working Directory",

        # Conversation management
        "rename_title": "Rename Chat",
        "rename_prompt": "Enter new name:",
        "new_chat_title": "New Chat",

        # Status
        "thinking_status": "Thinking...",
        "executing_status": "Executing: ",
        "error_status": "Error occurred",
    },
}


def T(key: str) -> str:
    """获取当前语言的翻译文本"""
    return TRANSLATIONS.get(_current_lang, TRANSLATIONS["zh"]).get(key, key)


def set_lang(lang: str):
    global _current_lang
    _current_lang = lang if lang in TRANSLATIONS else "zh"


def get_lang() -> str:
    return _current_lang
