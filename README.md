# MiMo Code Studio V2.0

> 基于小米 MiMo 模型的 AI 编程助手桌面客户端，支持代码生成、文件操作、语音朗读、多模型切换。

## 功能特性

1. **AI 对话** — 多轮对话、思考模式、上下文连续
2. **工具调用** — 文件创建/读写、目录浏览、命令执行、代码搜索
3. **多模型管理** — 自定义添加/删除模型，支持 mimo-v2.5-pro、mimo-v2.5 等
4. **工作目录** — 项目目录设置，文件树实时预览，支持无限层级展开
5. **语音朗读** — edge-tts 引擎，13 种中英文音色，语速/音量可调
6. **中英文切换** — 界面完整双语支持
7. **深色/浅色主题** — 双主题无缝切换
8. **对话管理** — 新建/切换/删除对话，历史记录持久保存
9. **System Prompt** — 自定义系统提示词，控制 AI 行为
10. **Logo 动画** — 品牌级视觉效果，粒子浮动 + 呼吸发光

## 截图展示

| 深色主题 | 浅色主题 | 成果展示 |
|:---:|:---:|:---:|
| ![深色主题](pic/1.png) | ![设置页面](pic/2.png) | ![浅色主题](pic/3.png) |

## 快速开始

### 环境要求

- Python 3.10+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API

1. 打开程序，点击左下角 **设置**
2. 填入你的 MiMo API 地址和 API Key
3. 添加想要使用的模型名称（如 `mimo-v2.5-pro`）
4. 点击 **保存设置**

### 启动程序

```bash
python main.py
```

或双击 `start.bat`（Windows，无控制台窗口）。

## 项目结构

```
MiMo-Code-Studio/
├── main.py                 # 程序入口
├── api_client.py           # MiMo API 客户端（流式请求 + 工具调用）
├── tts_engine.py           # 语音合成引擎（edge-tts）
├── audio_player.py         # 音频播放器（pygame）
├── config.py               # 配置管理
├── tools.py                # 工具实现（文件操作、命令执行、搜索）
├── start.bat               # Windows 启动脚本
├── requirements.txt        # Python 依赖
├── ui/
│   ├── app.py              # 主窗口
│   ├── chat_area.py        # 对话区域 + GlowLogo 动画
│   ├── sidebar.py          # 侧边栏（对话列表 + 文件树）
│   ├── input_bar.py        # 输入栏（语音控制 + 模型选择）
│   ├── settings_panel.py   # 设置面板
│   ├── widgets.py          # 自定义组件（工具卡片等）
│   ├── themes.py           # 主题配色定义
│   └── i18n.py             # 国际化（中英文）
├── data/                   # 用户数据（自动创建，已 gitignore）
├── pic/                    # 截图资源
└── README.md
```

## 技术栈

| 技术 | 用途 |
|---|---|
| Python 3.10+ | 主语言 |
| customtkinter | 现代化 GUI 框架 |
| edge-tts | 微软语音合成 |
| pygame | 音频播放 |
| requests | HTTP 请求 |
| chardet | 文件编码检测 |



## 致谢

- [小米 MiMo 团队](https://github.com/XiaomiMiMo) — MiMo 大模型提供Token
- Claude — 小牛马
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — 现代化 Tkinter UI
- [edge-tts](https://github.com/rany2/edge-tts) — 微软语音合成
- wuhenlol — 开发者
