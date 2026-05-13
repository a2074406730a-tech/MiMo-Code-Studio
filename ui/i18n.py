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
        "add_model": "添加",
        "model_placeholder": "输入模型名称",
        "stop_btn": "停止",
        "show": "显示",
        "hide": "隐藏",
        "select_workdir": "选择工作目录",
        "credit": "由 wuhenlol 制作并开源",

        # 对话管理
        "rename_title": "重命名对话",
        "rename_prompt": "输入新名称：",
        "new_chat_title": "新对话",

        # Token 统计
        "token_input": "输入",
        "token_output": "输出",
        "token_total": "总计",

        # 语音角色
        "voice_xiaoxiao": "晓晓（女声，温柔）",
        "voice_xiaoxiao_multi": "晓晓多语言（女声）",
        "voice_yunxi": "云希（男声，阳光）",
        "voice_yunjian": "云健（男声，沉稳）",
        "voice_xiaoyi": "晓艺（女声，活泼）",
        "voice_yunyang": "云扬（男声，新闻播报）",
        "voice_xiaochen": "晓辰（女声，知性）",
        "voice_xiaohan": "晓涵（女声，温暖）",
        "voice_jenny": "Jenny（女声，美式英语）",
        "voice_aria": "Aria（女声，美式英语）",
        "voice_guy": "Guy（男声，美式英语）",
        "voice_sara": "Sara（女声，美式英语）",
        "voice_davis": "Davis（男声，美式英语）",

        # 状态
        "thinking_status": "正在思考...",
        "executing_status": "正在执行: ",
        "error_status": "出错了",
        "paused_status": "对话已暂停",

        # 文件树
        "file_tree": "文件浏览",
        "file_tree_empty": "未设置工作目录",
        "file_tree_refresh": "刷新",
        "file_open": "打开",
        "file_delete": "删除",
        "file_delete_confirm": "删除不可恢复，确认删除？",
        "file_delete_confirm_title": "确认删除",
        "file_deleted": "已删除",
        "file_delete_failed": "删除失败",
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
        "add_model": "Add",
        "model_placeholder": "Enter model name",
        "stop_btn": "Stop",
        "show": "Show",
        "hide": "Hide",
        "select_workdir": "Select Working Directory",
        "credit": "Made and open-sourced by wuhenlol",

        # Conversation management
        "rename_title": "Rename Chat",
        "rename_prompt": "Enter new name:",
        "new_chat_title": "New Chat",

        # Token stats
        "token_input": "Input",
        "token_output": "Output",
        "token_total": "Total",

        # Voice roles
        "voice_xiaoxiao": "Xiaoxiao (Female, Gentle)",
        "voice_xiaoxiao_multi": "Xiaoxiao Multilingual (Female)",
        "voice_yunxi": "Yunxi (Male, Cheerful)",
        "voice_yunjian": "Yunjian (Male, Steady)",
        "voice_xiaoyi": "Xiaoyi (Female, Lively)",
        "voice_yunyang": "Yunyang (Male, News Anchor)",
        "voice_xiaochen": "Xiaochen (Female, Intellectual)",
        "voice_xiaohan": "Xiaohan (Female, Warm)",
        "voice_jenny": "Jenny (Female, US English)",
        "voice_aria": "Aria (Female, US English)",
        "voice_guy": "Guy (Male, US English)",
        "voice_sara": "Sara (Female, US English)",
        "voice_davis": "Davis (Male, US English)",

        # Status
        "thinking_status": "Thinking...",
        "executing_status": "Executing: ",
        "error_status": "Error occurred",
        "paused_status": "Paused",

        # File tree
        "file_tree": "Files",
        "file_tree_empty": "No working directory",
        "file_tree_refresh": "Refresh",
        "file_open": "Open",
        "file_delete": "Delete",
        "file_delete_confirm": "Cannot be undone. Confirm delete?",
        "file_delete_confirm_title": "Confirm Delete",
        "file_deleted": "Deleted",
        "file_delete_failed": "Delete failed",
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
