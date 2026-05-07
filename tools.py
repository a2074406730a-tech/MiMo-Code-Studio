"""工具实现模块 - 文件操作、命令执行、搜索"""

import os
import subprocess
import chardet


# 工具定义（发给 MiMo 的 tools 参数）
TOOLS_DEFINITION = [
    {
        "name": "read_file",
        "description": "读取指定路径的文件内容，支持任意编码自动检测",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "encoding": {"type": "string", "description": "文件编码，默认自动检测", "default": "auto"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "创建或覆盖写入文件，自动创建不存在的目录",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "编辑文件的指定部分，通过精确文本替换",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "old_text": {"type": "string", "description": "要替换的原文"},
                "new_text": {"type": "string", "description": "替换后的内容"}
            },
            "required": ["path", "old_text", "new_text"]
        }
    },
    {
        "name": "list_directory",
        "description": "列出目录下的文件和子目录，返回树形结构",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目录路径"},
                "recursive": {"type": "boolean", "description": "是否递归列出，默认false", "default": False}
            },
            "required": ["path"]
        }
    },
    {
        "name": "run_command",
        "description": "执行终端命令，实时捕获输出，超时60秒自动终止",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "命令字符串"},
                "working_dir": {"type": "string", "description": "工作目录，可选"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "search_files",
        "description": "在文件中搜索内容，支持文件过滤",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "path": {"type": "string", "description": "搜索目录"},
                "file_pattern": {"type": "string", "description": "文件过滤，如 *.py"}
            },
            "required": ["query", "path"]
        }
    }
]


def read_file(path: str, encoding: str = "auto") -> str:
    """读取文件内容"""
    if not os.path.exists(path):
        return f"错误：文件不存在 - {path}"
    if not os.path.isfile(path):
        return f"错误：路径不是文件 - {path}"
    try:
        if encoding == "auto":
            with open(path, "rb") as f:
                raw = f.read()
            detected = chardet.detect(raw)
            enc = detected.get("encoding", "utf-8") or "utf-8"
            return raw.decode(enc, errors="replace")
        else:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
    except Exception as e:
        return f"读取文件失败: {e}"


def write_file(path: str, content: str) -> str:
    """写入文件"""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件已写入: {path}"
    except Exception as e:
        return f"写入文件失败: {e}"


def edit_file(path: str, old_text: str, new_text: str) -> str:
    """编辑文件"""
    if not os.path.exists(path):
        return f"错误：文件不存在 - {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_text not in content:
            return "错误：未找到要替换的文本"
        new_content = content.replace(old_text, new_text, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return "文件已编辑成功"
    except Exception as e:
        return f"编辑文件失败: {e}"


def list_directory(path: str, recursive: bool = False) -> str:
    """列出目录结构"""
    if not os.path.exists(path):
        return f"错误：目录不存在 - {path}"
    if not os.path.isdir(path):
        return f"错误：路径不是目录 - {path}"
    try:
        lines = []
        if recursive:
            for root, dirs, files in os.walk(path):
                level = root.replace(path, "").count(os.sep)
                indent = "  " * level
                lines.append(f"{indent}{os.path.basename(root)}/")
                sub_indent = "  " * (level + 1)
                for f in files:
                    lines.append(f"{sub_indent}{f}")
        else:
            for item in sorted(os.listdir(path)):
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    lines.append(f"  {item}/")
                else:
                    lines.append(f"  {item}")
        return "\n".join(lines) if lines else "（空目录）"
    except Exception as e:
        return f"列出目录失败: {e}"


def run_command(command: str, working_dir: str = None) -> str:
    """执行终端命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=working_dir,
            encoding="utf-8",
            errors="replace",
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr
        if result.returncode != 0:
            output += f"\n[退出码: {result.returncode}]"
        return output or "（命令执行完成，无输出）"
    except subprocess.TimeoutExpired:
        return "错误：命令执行超时（60秒）"
    except Exception as e:
        return f"执行命令失败: {e}"


def search_files(query: str, path: str, file_pattern: str = None) -> str:
    """在文件中搜索内容"""
    if not os.path.exists(path):
        return f"错误：目录不存在 - {path}"
    results = []
    try:
        for root, dirs, files in os.walk(path):
            # 跳过隐藏目录和常见忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                       {'node_modules', '__pycache__', '.git', 'venv', '.venv'}]
            for fname in files:
                if file_pattern:
                    import fnmatch
                    if not fnmatch.fnmatch(fname, file_pattern):
                        continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                rel = os.path.relpath(fpath, path)
                                results.append(f"{rel}:{i}: {line.rstrip()}")
                                if len(results) >= 50:
                                    return "\n".join(results) + "\n...（结果过多，已截断）"
                except Exception:
                    continue
        return "\n".join(results) if results else "未找到匹配结果"
    except Exception as e:
        return f"搜索失败: {e}"


def execute_tool(name: str, params: dict) -> str:
    """执行指定工具"""
    if name == "read_file":
        return read_file(params["path"], params.get("encoding", "auto"))
    elif name == "write_file":
        return write_file(params["path"], params["content"])
    elif name == "edit_file":
        return edit_file(params["path"], params["old_text"], params["new_text"])
    elif name == "list_directory":
        return list_directory(params["path"], params.get("recursive", False))
    elif name == "run_command":
        return run_command(params["command"], params.get("working_dir"))
    elif name == "search_files":
        return search_files(params["query"], params["path"], params.get("file_pattern"))
    else:
        return f"未知工具: {name}"
