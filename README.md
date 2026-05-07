# MiMo Code Studio

> AI 编程助手桌面应用 — 基于 MiMo 大模型，支持代码编写、文件操作、命令执行、语音朗读

[English](./README_EN.md) | 中文

## 功能特性

- **AI 对话** — 支持流式输出，实时显示回复内容
- **工具调用** — 自动执行文件读写、代码编辑、目录浏览、终端命令、内容搜索
- **语音朗读** — 基于 Edge TTS，5 种中文语音人物，支持语速/音量调节
- **多对话管理** — 创建、切换、重命名、删除对话，历史记录持久化
- **深色/浅色主题** — 一键切换，自动保存偏好
- **Markdown 渲染** — 自动剥离格式标记，保留纯文本显示
- **表情过滤** — 朗读时自动过滤表情符号和特殊 Unicode 字符

## 界面预览

```
+----------------------------------------------------------+
|  MiMo Code Studio                              [浅色]    |
+----------+-----------------------------------------------+
| [新对话]  |  用户: 帮我写一个排序算法                        |
|          |                                               |
| 对话 1    |  MiMo: 好的，这是一个快速排序的实现...           |
| 对话 2    |       [朗读] [复制]                            |
| 对话 3    |                                               |
|          |  [工具] read_file → main.py                   |
|          |       执行完成                                 |
| [设置]    |  +------------------------------------------+|
|          |  | MiMo 正在思考...                          ||
|          |  +------------------------------------------+|
+----------+-----------------------------------------------+
|  晓晓(女声) | 语速 [----o----] | 音量 [------o--] | 自动朗读 |
|  [发送]                                                      |
+----------------------------------------------------------+
|  就绪                     | Token: 输入 1234 | 输出 567   |
+----------------------------------------------------------+
```

## 快速开始

### 环境要求

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Windows | 10/11 | 仅支持 Windows |
| Python | 3.10+ | 推荐 3.12 |
| PowerShell | 5.1+ | 用于安装和启动 |
| pip | 随 Python 自带 | 包管理器 |
| Git | 2.30+ | 克隆仓库（可选） |

### 第一步：克隆仓库

```powershell
cd mimo-speaker

```

### 第二步：检查 Python 环境

```powershell
# 检查 Python 版本（需要 3.10+）
python --version

# 如果没有 Python，从 Microsoft Store 安装
winget install Python.Python.3.12

# 或者从官网下载：https://www.python.org/downloads/
# 安装时务必勾选 "Add Python to PATH"
```

### 第三步：创建虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果遇到执行策略错误，先运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

激活成功后，终端提示符会显示 `(venv)` 前缀。

### 第四步：安装依赖

```powershell
# 升级 pip
python -m pip install --upgrade pip

# 安装所有依赖
pip install customtkinter requests edge-tts pygame chardet pygments
```

**依赖说明：**

| 包名 | 版本 | 用途 |
|------|------|------|
| `customtkinter` | 5.2+ | 现代化 Tkinter GUI 框架 |
| `requests` | 2.28+ | HTTP 请求（调用 MiMo API） |
| `edge-tts` | 6.1+ | 微软 Edge TTS 语音合成 |
| `pygame` | 2.5+ | 音频播放引擎 |
| `chardet` | 5.0+ | 文件编码自动检测 |
| `pygments` | 2.14+ | 代码语法高亮 |

或者使用 requirements.txt 一键安装：

```powershell
pip install -r requirements.txt
```

### 第五步：配置 API

```powershell
# 复制示例配置
Copy-Item data\settings.example.json data\settings.json
```

编辑 `data/settings.json`，填入你的 API 信息：

```json
{
  "api_url": "https://your-api-endpoint/v1/messages",
  "api_key": "your-api-key-here",
  "model": "mimo-v2.5-pro",
  "max_tokens": 4096
}
```

### 第六步：启动应用

**方式一：双击启动（推荐）**

双击项目根目录下的 `start.bat`

**方式二：PowerShell 启动**

```powershell
# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 启动应用
python main.py
```

**方式三：不激活虚拟环境直接启动**

```powershell
.\venv\Scripts\python.exe main.py
```

### 运行测试

```powershell
# 激活虚拟环境后
python test.py
```

测试覆盖 10 个模块、56 个用例：配置管理、工具模块、消息发送、工具调用解析、TTS 语音合成、音频播放器、文本处理、多对话管理、工具调用集成、稳定性测试。

## 项目结构

```
mimo-speaker/
├── main.py                    # 入口文件
├── config.py                  # 配置管理 + 对话持久化
├── api_client.py              # MiMo API 客户端（流式 SSE + 工具调用）
├── tools.py                   # 工具定义与实现（文件/命令/搜索）
├── tts_engine.py              # Edge TTS 语音合成引擎
├── audio_player.py            # Pygame 音频播放器
├── start.bat                  # Windows 启动脚本
├── test.py                    # 自动化测试脚本（56 个用例）
├── requirements.txt           # Python 依赖清单
├── .gitignore                 # Git 忽略规则
├── README.md                  # 中文文档
├── README_EN.md               # 英文文档
├── data/
│   ├── settings.example.json  # 配置模板（安全，可提交）
│   ├── settings.json          # 用户配置（含 API Key，已 git 忽略）
│   └── conversations.json     # 对话记录（已 git 忽略）
└── ui/
    ├── __init__.py
    ├── app.py                 # 主窗口
    ├── chat_area.py           # 对话区域 + 消息气泡
    ├── sidebar.py             # 侧边栏 + 对话列表
    ├── input_bar.py           # 输入栏 + 语音控制
    ├── settings_panel.py      # 设置面板
    ├── themes.py              # 深色/浅色主题配色
    ├── widgets.py             # 自定义组件（ToolCallCard 等）
    └── markdown_renderer.py   # Markdown 渲染器
```

## 工具调用

AI 助手在对话中可以自动调用以下工具：

| 工具 | 说明 | 示例 |
|------|------|------|
| `read_file` | 读取文件，自动检测编码 | "帮我看看 main.py 的内容" |
| `write_file` | 写入文件，自动创建目录 | "创建一个 hello.py" |
| `edit_file` | 精确文本替换 | "把第 10 行的 print 改成 logging" |
| `list_directory` | 列出目录结构 | "看看项目里有哪些文件" |
| `run_command` | 执行终端命令（60s 超时） | "运行 python --version" |
| `search_files` | 文件内容搜索 | "搜索所有用了 requests 的文件" |

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| GUI 框架 | customtkinter | 基于 Tkinter 的现代化 UI |
| AI 接口 | Anthropic Messages API | 流式 SSE 协议 |
| 语音合成 | Edge TTS | 微软免费 TTS 服务 |
| 音频播放 | Pygame | 跨平台音频引擎 |
| 编码检测 | chardet | 自动识别文件编码 |
| HTTP 客户端 | requests | API 通信 |
| Python | 3.10+ | 最低版本要求 |

## 常见问题

### PowerShell 执行策略错误

```powershell
# 错误：无法加载文件，因为在此系统上禁止运行脚本
# 解决：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### pip install 超时

```powershell
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### edge-tts 安装失败

```powershell
# 确保 Python 版本 >= 3.10
python --version

# 单独安装 edge-tts
pip install edge-tts --no-cache-dir
```

### pygame 初始化失败

```powershell
# 重新安装 pygame
pip uninstall pygame
pip install pygame --no-cache-dir
```

### 应用启动后白屏/黑屏

```powershell
# 检查 customtkinter 版本
pip show customtkinter

# 升级到最新版
pip install customtkinter --upgrade
```

## 依赖安装完整指令

### PowerShell 一键安装（推荐）

```powershell
# 1. 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. 升级 pip
python -m pip install --upgrade pip

# 3. 安装所有依赖
pip install customtkinter>=5.2.0 requests>=2.28.0 edge-tts>=6.1.0 pygame>=2.5.0 chardet>=5.0.0 pygments>=2.14.0

# 4. 或使用 requirements.txt
pip install -r requirements.txt
```

### 国内镜像加速

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 依赖版本清单

| 包名 | 最低版本 | 用途 |
|------|----------|------|
| customtkinter | 5.2.0 | GUI 框架 |
| requests | 2.28.0 | HTTP 请求 |
| edge-tts | 6.1.0 | 语音合成 |
| pygame | 2.5.0 | 音频播放 |
| chardet | 5.0.0 | 编码检测 |
| pygments | 2.14.0 | 代码高亮 |

