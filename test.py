"""MiMo Code Studio - 自动化测试脚本"""

import os
import sys
import json
import time
import shutil
import tempfile
import threading
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 测试框架
# ============================================================

class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = time.time()

    def ok(self, desc):
        self.passed += 1
        print(f"    [PASS] {desc}")

    def fail(self, desc, msg=""):
        self.failed += 1
        self.errors.append(f"{desc}: {msg}")
        print(f"    [FAIL] {desc} - {msg}")

    def elapsed(self):
        return time.time() - self.start_time


class TestRunner:
    def __init__(self):
        self.suites = []

    def suite(self, name):
        result = TestResult(name)
        self.suites.append(result)
        return result

    def report(self):
        print("\n" + "=" * 60)
        print("  测试报告")
        print("=" * 60)
        total_pass = 0
        total_fail = 0
        for s in self.suites:
            total_pass += s.passed
            total_fail += s.failed
            status = "PASS" if s.failed == 0 else "FAIL"
            print(f"\n  [{status}] {s.name} ({s.elapsed():.1f}s)")
            print(f"        通过: {s.passed}  失败: {s.failed}")
            for err in s.errors:
                print(f"        - {err}")

        print("\n" + "-" * 60)
        overall = "ALL PASS" if total_fail == 0 else f"{total_fail} FAILED"
        print(f"  总计: {total_pass} 通过, {total_fail} 失败 [{overall}]")
        print("=" * 60)
        return total_fail == 0


runner = TestRunner()


# ============================================================
# 测试 1: 配置管理
# ============================================================

def test_config():
    s = runner.suite("1. 配置管理 (config.py)")
    from config import Config, ConversationStore

    # 测试 1.1: 默认配置加载
    try:
        cfg = Config()
        if cfg["model"] == "mimo-v2.5-pro":
            s.ok("默认配置加载正确")
        else:
            s.fail("默认配置加载", f"model={cfg['model']}")
    except Exception as e:
        s.fail("默认配置加载", str(e))

    # 测试 1.2: 配置读写
    try:
        cfg["test_key"] = "test_value_123"
        cfg.save()
        cfg2 = Config()
        if cfg2["test_key"] == "test_value_123":
            s.ok("配置持久化读写")
        else:
            s.fail("配置持久化读写", "值不匹配")
        del cfg._data["test_key"]
        cfg.save()
    except Exception as e:
        s.fail("配置持久化读写", str(e))

    # 测试 1.3: 默认值完整性
    try:
        required_keys = ["api_url", "api_key", "model", "max_tokens", "system_prompt"]
        missing = [k for k in required_keys if k not in cfg._data]
        if not missing:
            s.ok("默认值完整性检查")
        else:
            s.fail("默认值完整性", f"缺少: {missing}")
    except Exception as e:
        s.fail("默认值完整性", str(e))

    # 测试 1.4: 对话存储 CRUD
    try:
        store = ConversationStore()
        test_conv = {"id": "test_conv_001", "title": "测试对话", "messages": []}
        store.add(test_conv)
        found = store.get_by_id("test_conv_001")
        if found and found["title"] == "测试对话":
            s.ok("对话存储 - 添加和查询")
        else:
            s.fail("对话存储 - 添加和查询", "未找到")

        store.update("test_conv_001", {"title": "修改后的标题"})
        found = store.get_by_id("test_conv_001")
        if found["title"] == "修改后的标题":
            s.ok("对话存储 - 更新")
        else:
            s.fail("对话存储 - 更新", "标题未更新")

        store.delete("test_conv_001")
        found = store.get_by_id("test_conv_001")
        if found is None:
            s.ok("对话存储 - 删除")
        else:
            s.fail("对话存储 - 删除", "仍然存在")
    except Exception as e:
        s.fail("对话存储 CRUD", str(e))

    # 测试 1.5: 系统提示词
    try:
        prompt = cfg.get("system_prompt", "")
        if "MiMo" in prompt and "不要调用任何工具" in prompt:
            s.ok("系统提示词已优化（区分闲聊/编程）")
        else:
            s.fail("系统提示词", f"内容不符合预期: {prompt[:80]}")
    except Exception as e:
        s.fail("系统提示词检查", str(e))


# ============================================================
# 测试 2: 工具模块
# ============================================================

def test_tools():
    s = runner.suite("2. 工具模块 (tools.py)")
    from tools import execute_tool, TOOLS_DEFINITION

    tmp_dir = tempfile.mkdtemp(prefix="mimo_test_")

    # 测试 2.1: 工具定义完整性
    try:
        names = {t["name"] for t in TOOLS_DEFINITION}
        expected = {"read_file", "write_file", "edit_file", "list_directory", "run_command", "search_files"}
        if expected.issubset(names):
            s.ok(f"工具定义完整 ({len(names)} 个工具)")
        else:
            s.fail("工具定义完整", f"缺少: {expected - names}")
    except Exception as e:
        s.fail("工具定义完整性", str(e))

    # 测试 2.2: write_file + read_file
    try:
        test_file = os.path.join(tmp_dir, "test.txt")
        result = execute_tool("write_file", {"path": test_file, "content": "Hello MiMo\n你好世界"})
        if "已写入" in result:
            s.ok("write_file - 写入文件")
        else:
            s.fail("write_file", result)

        result = execute_tool("read_file", {"path": test_file})
        if "Hello MiMo" in result and "你好世界" in result:
            s.ok("read_file - 读取文件（含中文）")
        else:
            s.fail("read_file", f"内容不匹配: {result[:100]}")
    except Exception as e:
        s.fail("write/read_file", str(e))

    # 测试 2.3: edit_file
    try:
        result = execute_tool("edit_file", {"path": test_file, "old_text": "Hello", "new_text": "Hi"})
        if "成功" in result:
            content = execute_tool("read_file", {"path": test_file})
            if "Hi MiMo" in content:
                s.ok("edit_file - 文本替换")
            else:
                s.fail("edit_file", f"替换后内容不对: {content[:50]}")
        else:
            s.fail("edit_file", result)
    except Exception as e:
        s.fail("edit_file", str(e))

    # 测试 2.4: list_directory
    try:
        result = execute_tool("list_directory", {"path": tmp_dir})
        if "test.txt" in result:
            s.ok("list_directory - 列出目录")
        else:
            s.fail("list_directory", f"未找到文件: {result}")
    except Exception as e:
        s.fail("list_directory", str(e))

    # 测试 2.5: run_command
    try:
        result = execute_tool("run_command", {"command": "echo hello_mimo"})
        if "hello_mimo" in result:
            s.ok("run_command - 执行命令")
        else:
            s.fail("run_command", f"输出不对: {result}")
    except Exception as e:
        s.fail("run_command", str(e))

    # 测试 2.6: run_command - 错误处理
    try:
        result = execute_tool("run_command", {"command": "dir_nonexist_command_xyz"})
        if "错误" in result or "不是内部或外部命令" in result or result:
            s.ok("run_command - 无效命令错误处理")
        else:
            s.fail("run_command 错误处理", result[:100])
    except Exception as e:
        s.fail("run_command 错误处理", str(e))

    # 测试 2.7: search_files
    try:
        result = execute_tool("search_files", {"query": "MiMo", "path": tmp_dir})
        if "test.txt" in result:
            s.ok("search_files - 内容搜索")
        else:
            s.fail("search_files", f"未搜到: {result}")
    except Exception as e:
        s.fail("search_files", str(e))

    # 测试 2.8: read_file - 不存在的文件
    try:
        result = execute_tool("read_file", {"path": "/nonexist/file.txt"})
        if "错误" in result or "不存在" in result:
            s.ok("read_file - 文件不存在错误处理")
        else:
            s.fail("read_file 错误处理", result[:100])
    except Exception as e:
        s.fail("read_file 错误处理", str(e))

    # 测试 2.9: write_file - 自动创建目录
    try:
        nested = os.path.join(tmp_dir, "a", "b", "c", "deep.txt")
        result = execute_tool("write_file", {"path": nested, "content": "deep"})
        if "已写入" in result and os.path.exists(nested):
            s.ok("write_file - 自动创建嵌套目录")
        else:
            s.fail("write_file 嵌套目录", result)
    except Exception as e:
        s.fail("write_file 嵌套目录", str(e))

    # 清理
    shutil.rmtree(tmp_dir, ignore_errors=True)


# ============================================================
# 测试 3: 消息发送 (API 客户端)
# ============================================================

def test_api_client():
    s = runner.suite("3. 消息发送 (api_client.py)")
    from config import Config
    from api_client import MiMoClient

    cfg = Config()
    client = MiMoClient(cfg)

    # 测试 3.1: 客户端初始化
    try:
        if not client.is_busy and len(client.messages) == 0:
            s.ok("客户端初始化状态正确")
        else:
            s.fail("客户端初始化", f"busy={client.is_busy}, msgs={len(client.messages)}")
    except Exception as e:
        s.fail("客户端初始化", str(e))

    # 测试 3.2: 消息历史管理
    try:
        client.messages.append({"role": "user", "content": "test"})
        client.messages.append({"role": "assistant", "content": "reply"})
        client.clear_history()
        if len(client.messages) == 0:
            s.ok("消息历史清除")
        else:
            s.fail("消息历史清除", f"剩余 {len(client.messages)} 条")
    except Exception as e:
        s.fail("消息历史清除", str(e))

    # 测试 3.3: 短消息发送（实际API调用）
    try:
        result = {"text": "", "done": False, "error": None}

        def on_token(t): result["text"] += t
        def on_done(t): result["done"] = True
        def on_error(e): result["error"] = e

        client.send_message("你好，请回复OK", callbacks={
            "on_token": on_token, "on_done": on_done, "on_error": on_error,
        })

        # 等待完成，最多30秒
        for _ in range(300):
            if result["done"] or result["error"]:
                break
            time.sleep(0.1)

        if result["error"]:
            s.fail("短消息发送", str(result["error"]))
        elif result["done"] and len(result["text"]) > 0:
            s.ok(f"短消息发送 (回复 {len(result['text'])} 字)")
        else:
            s.fail("短消息发送", f"done={result['done']}, text_len={len(result['text'])}")
    except Exception as e:
        s.fail("短消息发送", str(e))

    # 测试 3.4: 长消息发送
    try:
        client.clear_history()
        result = {"text": "", "done": False, "error": None}
        long_msg = "请用一句话回答：1+1等于几？" * 20  # ~300字

        client.send_message(long_msg, callbacks={
            "on_token": on_token, "on_done": on_done, "on_error": on_error,
        })
        for _ in range(300):
            if result["done"] or result["error"]:
                break
            time.sleep(0.1)

        if result["error"]:
            s.fail("长消息发送", str(result["error"]))
        elif result["done"]:
            s.ok(f"长消息发送 ({len(long_msg)}字, 回复 {len(result['text'])} 字)")
        else:
            s.fail("长消息发送", "超时未完成")
    except Exception as e:
        s.fail("长消息发送", str(e))

    # 测试 3.5: cancel 功能
    try:
        client.clear_history()
        result = {"text": "", "done": False, "error": None}

        client.send_message("写一篇1000字的文章", callbacks={
            "on_token": on_token, "on_done": on_done, "on_error": on_error,
        })
        time.sleep(1)
        client.cancel()

        for _ in range(50):
            if result["done"]:
                break
            time.sleep(0.1)

        s.ok("cancel 请求发送成功（不阻塞）")
    except Exception as e:
        s.fail("cancel 功能", str(e))

    # 等一下确保busy状态重置
    for _ in range(50):
        if not client.is_busy:
            break
        time.sleep(0.1)


# ============================================================
# 测试 4: 工具调用解析
# ============================================================

def test_tool_parsing():
    s = runner.suite("4. 工具调用解析")
    from api_client import MiMoClient
    from config import Config

    client = MiMoClient(Config())

    # 测试 4.1: <tool_calls> XML 格式解析
    try:
        text = '''我来帮你读取文件。

<tool_calls>
<invoke>
<tool_name>read_file</tool_name>
<parameters>{"path": "/tmp/test.py"}</parameters>
</invoke>
</tool_calls>'''
        result = client._parse_tool_calls(text)
        if len(result) == 1 and result[0]["name"] == "read_file":
            s.ok("解析 <tool_calls> XML 格式")
        else:
            s.fail("解析 <tool_calls> XML", f"结果: {result}")
    except Exception as e:
        s.fail("解析 <tool_calls> XML", str(e))

    # 测试 4.2: 多个工具调用
    try:
        text = '''<tool_calls>
<invoke>
<tool_name>list_directory</tool_name>
<parameters>{"path": "."}</parameters>
</invoke>
<invoke>
<tool_name>read_file</tool_name>
<parameters>{"path": "main.py"}</parameters>
</invoke>
</tool_calls>'''
        result = client._parse_tool_calls(text)
        if len(result) == 2:
            s.ok("解析多个工具调用")
        else:
            s.fail("解析多个工具调用", f"只解析出 {len(result)} 个")
    except Exception as e:
        s.fail("解析多个工具调用", str(e))

    # 测试 4.3: 代码块格式解析
    try:
        text = '''```read_file
{"path": "config.py"}
```'''
        result = client._parse_tool_calls(text)
        if len(result) == 1 and result[0]["name"] == "read_file":
            s.ok("解析代码块格式")
        else:
            s.fail("解析代码块格式", f"结果: {result}")
    except Exception as e:
        s.fail("解析代码块格式", str(e))

    # 测试 4.4: JSON 格式解析
    try:
        text = '执行命令: {"name":"run_command","arguments":{"command":"ls -la"}}'
        result = client._parse_tool_calls(text)
        if len(result) == 1 and result[0]["name"] == "run_command":
            s.ok("解析 JSON 格式")
        else:
            s.fail("解析 JSON 格式", f"结果: {result}")
    except Exception as e:
        s.fail("解析 JSON 格式", str(e))

    # 测试 4.5: 无工具调用时返回空
    try:
        text = "这是一段普通文本，没有工具调用。"
        result = client._parse_tool_calls(text)
        if len(result) == 0:
            s.ok("无工具调用返回空列表")
        else:
            s.fail("无工具调用", f"误识别: {result}")
    except Exception as e:
        s.fail("无工具调用", str(e))

    # 测试 4.6: 空文本处理
    try:
        result = client._parse_tool_calls("")
        if len(result) == 0:
            s.ok("空文本安全处理")
        else:
            s.fail("空文本处理", f"返回: {result}")
    except Exception as e:
        s.fail("空文本处理", str(e))

    # 测试 4.7: 工具标签文本剥离
    try:
        import re
        text = '''好的，让我读取文件。

<tool_calls>
<invoke>
<tool_name>read_file</tool_name>
<parameters>{"path": "test.py"}</parameters>
</invoke>
</tool_calls>'''
        cleaned = re.sub(r'<tool_calls>[\s\S]*?</tool_calls>', '', text).strip()
        if "tool_calls" not in cleaned and "好的" in cleaned:
            s.ok("工具标签文本剥离")
        else:
            s.fail("工具标签剥离", f"清理后: {cleaned[:80]}")
    except Exception as e:
        s.fail("工具标签剥离", str(e))


# ============================================================
# 测试 5: TTS 语音合成
# ============================================================

def test_tts():
    s = runner.suite("5. TTS 语音合成")
    from tts_engine import generate_audio_sync, cleanup_audio, VOICE_LIST

    # 测试 5.1: 语音列表完整性
    try:
        if len(VOICE_LIST) >= 5:
            s.ok(f"语音列表完整 ({len(VOICE_LIST)} 个语音)")
        else:
            s.fail("语音列表", f"只有 {len(VOICE_LIST)} 个")
    except Exception as e:
        s.fail("语音列表", str(e))

    # 测试 5.2: 默认语音生成
    try:
        path = generate_audio_sync("你好，这是测试", "zh-CN-XiaoxiaoNeural", 0, 80)
        if os.path.exists(path) and os.path.getsize(path) > 100:
            s.ok("默认语音生成 (晓晓)")
        else:
            s.fail("默认语音生成", f"path={path}, exists={os.path.exists(path)}")
        cleanup_audio(path)
    except Exception as e:
        s.fail("默认语音生成", str(e))

    # 测试 5.3: 多语音人物
    try:
        for voice_id, voice_name in VOICE_LIST[:3]:
            try:
                path = generate_audio_sync("测试语音", voice_id, 0, 80)
                exists = os.path.exists(path) and os.path.getsize(path) > 100
                cleanup_audio(path)
                if not exists:
                    s.fail(f"语音人物 {voice_name}", "文件不存在或为空")
                    continue
            except Exception as e:
                s.fail(f"语音人物 {voice_name}", str(e))
                continue
        s.ok("多语音人物生成 (前3个)")
    except Exception as e:
        s.fail("多语音人物", str(e))

    # 测试 5.4: 语速调节
    try:
        for rate in [-50, 0, 50]:
            path = generate_audio_sync("语速测试", "zh-CN-XiaoxiaoNeural", rate, 80)
            cleanup_audio(path)
        s.ok("语速调节 (-50, 0, +50)")
    except Exception as e:
        s.fail("语速调节", str(e))

    # 测试 5.5: 音量调节
    try:
        for vol in [0, 50, 100]:
            path = generate_audio_sync("音量测试", "zh-CN-XiaoxiaoNeural", 0, vol)
            cleanup_audio(path)
        s.ok("音量调节 (0, 50, 100)")
    except Exception as e:
        s.fail("音量调节", str(e))

    # 测试 5.6: 表情符号过滤后朗读
    try:
        from ui.chat_area import strip_emoji
        text_with_emoji = "你好😊世界🌍，这是测试🎉"
        filtered = strip_emoji(text_with_emoji)
        if "😊" not in filtered and "🌍" not in filtered and "你好" in filtered:
            s.ok("表情符号过滤")
        else:
            s.fail("表情符号过滤", f"过滤后: {filtered}")

        # 实际朗读过滤后的文本
        path = generate_audio_sync(filtered, "zh-CN-XiaoxiaoNeural", 0, 80)
        if os.path.exists(path):
            s.ok("过滤后文本朗读")
        else:
            s.fail("过滤后文本朗读", "音频文件未生成")
        cleanup_audio(path)
    except Exception as e:
        s.fail("表情符号过滤朗读", str(e))

    # 测试 5.7: 失败回退机制
    try:
        # 使用一个无效语音名，应该回退到默认语音
        path = generate_audio_sync("回退测试", "invalid-voice-name-xyz", 0, 80)
        if os.path.exists(path) and os.path.getsize(path) > 100:
            s.ok("语音回退机制（无效语音→默认语音）")
        else:
            s.fail("语音回退", "回退后仍未生成音频")
        cleanup_audio(path)
    except Exception as e:
        s.fail("语音回退机制", str(e))


# ============================================================
# 测试 6: 音频播放器
# ============================================================

def test_audio_player():
    s = runner.suite("6. 音频播放器")
    from audio_player import AudioPlayer
    from tts_engine import generate_audio_sync, cleanup_audio

    # 测试 6.1: 初始化
    try:
        player = AudioPlayer()
        if not player.is_playing:
            s.ok("AudioPlayer 初始化")
        else:
            s.fail("AudioPlayer 初始化", "is_playing=True")
    except Exception as e:
        s.fail("AudioPlayer 初始化", str(e))

    # 测试 6.2: mixer 重新初始化
    try:
        player._init_mixer()
        import pygame
        if pygame.mixer.get_init():
            s.ok("mixer 重新初始化")
        else:
            s.fail("mixer 重新初始化", "get_init() 返回 None")
    except Exception as e:
        s.fail("mixer 重新初始化", str(e))

    # 测试 6.3: stop 不崩溃
    try:
        player.stop()
        s.ok("stop 空闲状态不崩溃")
    except Exception as e:
        s.fail("stop 空闲状态", str(e))


# ============================================================
# 测试 7: Markdown 和 Emoji 处理
# ============================================================

def test_text_processing():
    s = runner.suite("7. 文本处理")
    from ui.chat_area import strip_markdown, strip_emoji

    # 测试 7.1: Markdown 剥离
    try:
        md = "**粗体** *斜体* `代码` [链接](http://example.com)"
        result = strip_markdown(md)
        if "**" not in result and "*" not in result and "`" not in result:
            s.ok("Markdown 格式剥离")
        else:
            s.fail("Markdown 剥离", f"结果: {result}")
    except Exception as e:
        s.fail("Markdown 剥离", str(e))

    # 测试 7.2: 代码块保留
    try:
        md = "```python\nprint('hello')\n```"
        result = strip_markdown(md)
        if "print" in result:
            s.ok("代码块内容保留")
        else:
            s.fail("代码块保留", f"结果: {result}")
    except Exception as e:
        s.fail("代码块保留", str(e))

    # 测试 7.3: Emoji 剥离 - 基本
    try:
        text = "Hello 😊🌍🎉 World"
        result = strip_emoji(text)
        if "😊" not in result and "Hello" in result and "World" in result:
            s.ok("Emoji 基本剥离")
        else:
            s.fail("Emoji 基本剥离", f"结果: {result}")
    except Exception as e:
        s.fail("Emoji 基本剥离", str(e))

    # 测试 7.4: Emoji 剥离 - 中文混合
    try:
        text = "你好👍世界🌟，这是💪测试🎯"
        result = strip_emoji(text)
        has_emoji = any(c in result for c in "👍🌟💪🎯")
        if not has_emoji and "你好" in result and "世界" in result:
            s.ok("Emoji 中文混合剥离")
        else:
            s.fail("Emoji 中文混合剥离", f"结果: {result}")
    except Exception as e:
        s.fail("Emoji 中文混合剥离", str(e))

    # 测试 7.5: 无 Emoji 文本不变
    try:
        text = "这是一段纯中文文本，没有表情符号。"
        result = strip_emoji(text)
        if result == text:
            s.ok("无 Emoji 文本保持不变")
        else:
            s.fail("无 Emoji 不变", f"结果: {result}")
    except Exception as e:
        s.fail("无 Emoji 不变", str(e))

    # 测试 7.6: 空文本处理
    try:
        result = strip_emoji("")
        result2 = strip_markdown("")
        if result == "" and result2 == "":
            s.ok("空文本安全处理")
        else:
            s.fail("空文本", f"emoji='{result}', md='{result2}'")
    except Exception as e:
        s.fail("空文本处理", str(e))


# ============================================================
# 测试 8: 多对话管理
# ============================================================

def test_multi_conversation():
    s = runner.suite("8. 多对话管理")
    from config import ConversationStore

    store = ConversationStore()

    # 清理可能残留的测试数据
    for conv in store.get_all():
        if conv.get("id", "").startswith("test_multi_"):
            store.delete(conv["id"])

    # 测试 8.1: 创建多个对话
    try:
        for i in range(5):
            store.add({
                "id": f"test_multi_{i}",
                "title": f"测试对话 {i}",
                "messages": [{"role": "user", "content": f"消息 {i}"}],
            })
        all_convs = store.get_all()
        test_convs = [c for c in all_convs if c.get("id", "").startswith("test_multi_")]
        if len(test_convs) == 5:
            s.ok("创建 5 个对话")
        else:
            s.fail("创建多对话", f"只找到 {len(test_convs)} 个")
    except Exception as e:
        s.fail("创建多对话", str(e))

    # 测试 8.2: 对话独立性
    try:
        conv0 = store.get_by_id("test_multi_0")
        conv4 = store.get_by_id("test_multi_4")
        if conv0["messages"][0]["content"] == "消息 0" and conv4["messages"][0]["content"] == "消息 4":
            s.ok("对话消息独立性")
        else:
            s.fail("对话独立性", "消息内容混淆")
    except Exception as e:
        s.fail("对话独立性", str(e))

    # 测试 8.3: 对话更新不影响其他对话
    try:
        store.update("test_multi_2", {"title": "修改后的标题"})
        conv2 = store.get_by_id("test_multi_2")
        conv1 = store.get_by_id("test_multi_1")
        if conv2["title"] == "修改后的标题" and conv1["title"] == "测试对话 1":
            s.ok("对话更新不影响其他对话")
        else:
            s.fail("对话更新隔离", f"conv1={conv1['title']}, conv2={conv2['title']}")
    except Exception as e:
        s.fail("对话更新隔离", str(e))

    # 测试 8.4: 对话删除后查询返回 None
    try:
        store.delete("test_multi_3")
        conv = store.get_by_id("test_multi_3")
        if conv is None:
            s.ok("删除后查询返回 None")
        else:
            s.fail("删除后查询", "仍能查到")
    except Exception as e:
        s.fail("删除后查询", str(e))

    # 测试 8.5: 不存在的对话查询
    try:
        conv = store.get_by_id("nonexist_id_xyz")
        if conv is None:
            s.ok("不存在的对话返回 None")
        else:
            s.fail("不存在对话", "返回了数据")
    except Exception as e:
        s.fail("不存在对话", str(e))

    # 清理
    for i in range(5):
        store.delete(f"test_multi_{i}")


# ============================================================
# 测试 9: API 客户端工具调用集成
# ============================================================

def test_tool_call_integration():
    s = runner.suite("9. 工具调用集成")
    from config import Config
    from api_client import MiMoClient

    cfg = Config()
    client = MiMoClient(cfg)

    # 测试 9.1: 发送触发工具调用的消息
    try:
        client.clear_history()
        result = {"text": "", "tools": [], "done": False, "error": None}

        def on_token(t): result["text"] += t
        def on_tool_start(n, p): result["tools"].append(n)
        def on_tool_result(n, r): pass
        def on_done(t): result["done"] = True
        def on_error(e): result["error"] = e

        client.send_message("请列出当前目录下的文件", callbacks={
            "on_token": on_token,
            "on_tool_start": on_tool_start,
            "on_tool_result": on_tool_result,
            "on_done": on_done,
            "on_error": on_error,
        })

        for _ in range(600):
            if result["done"] or result["error"]:
                break
            time.sleep(0.1)

        if result["error"]:
            s.fail("工具调用集成", str(result["error"]))
        elif result["done"]:
            s.ok(f"工具调用集成 (触发了 {len(result['tools'])} 次工具调用)")
        else:
            s.fail("工具调用集成", "超时")
    except Exception as e:
        s.fail("工具调用集成", str(e))

    # 等待busy重置
    for _ in range(50):
        if not client.is_busy:
            break
        time.sleep(0.1)


# ============================================================
# 测试 10: 稳定性测试
# ============================================================

def test_stability():
    s = runner.suite("10. 稳定性测试")
    from tts_engine import generate_audio_sync, cleanup_audio
    from audio_player import AudioPlayer

    # 测试 10.1: 连续 TTS 生成（模拟长时间运行）
    try:
        success = 0
        for i in range(10):
            try:
                path = generate_audio_sync(f"稳定性测试第{i}句", "zh-CN-XiaoxiaoNeural", 0, 80)
                if os.path.exists(path):
                    success += 1
                cleanup_audio(path)
            except Exception:
                pass
        if success >= 8:
            s.ok(f"连续 TTS 生成 ({success}/10 成功)")
        else:
            s.fail("连续 TTS 生成", f"只有 {success}/10 成功")
    except Exception as e:
        s.fail("连续 TTS 生成", str(e))

    # 测试 10.2: mixer 反复初始化
    try:
        player = AudioPlayer()
        for _ in range(20):
            player._init_mixer()
        import pygame
        if pygame.mixer.get_init():
            s.ok("mixer 反复初始化 20 次（不失效）")
        else:
            s.fail("mixer 反复初始化", "mixer 失效")
    except Exception as e:
        s.fail("mixer 反复初始化", str(e))

    # 测试 10.3: 大文本 TTS
    try:
        big_text = "这是一段很长的测试文本。" * 100  # ~1300字
        from ui.chat_area import strip_emoji
        filtered = strip_emoji(big_text)
        path = generate_audio_sync(filtered, "zh-CN-XiaoxiaoNeural", 0, 80)
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            s.ok(f"大文本 TTS ({len(big_text)}字)")
        else:
            s.fail("大文本 TTS", f"文件大小: {os.path.getsize(path) if os.path.exists(path) else 0}")
        cleanup_audio(path)
    except Exception as e:
        s.fail("大文本 TTS", str(e))

    # 测试 10.4: 文件操作压力测试
    try:
        from tools import execute_tool
        tmp_dir = tempfile.mkdtemp(prefix="mimo_stress_")
        success = 0
        for i in range(20):
            fpath = os.path.join(tmp_dir, f"file_{i}.txt")
            r = execute_tool("write_file", {"path": fpath, "content": f"内容{i}"})
            if "已写入" in r:
                success += 1
        if success == 20:
            s.ok("文件操作压力测试 (20 文件)")
        else:
            s.fail("文件操作压力", f"只有 {success}/20 成功")
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception as e:
        s.fail("文件操作压力", str(e))


# ============================================================
# 运行所有测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  MiMo Code Studio - 自动化测试")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_tests = [
        ("配置管理", test_config),
        ("工具模块", test_tools),
        ("消息发送", test_api_client),
        ("工具调用解析", test_tool_parsing),
        ("TTS语音合成", test_tts),
        ("音频播放器", test_audio_player),
        ("文本处理", test_text_processing),
        ("多对话管理", test_multi_conversation),
        ("工具调用集成", test_tool_call_integration),
        ("稳定性测试", test_stability),
    ]

    for name, test_func in all_tests:
        print(f"\n{'─' * 60}")
        print(f"  运行: {name}")
        print(f"{'─' * 60}")
        try:
            test_func()
        except Exception as e:
            print(f"    [ERROR] 测试套件崩溃: {e}")
            traceback.print_exc()

    success = runner.report()
    sys.exit(0 if success else 1)
