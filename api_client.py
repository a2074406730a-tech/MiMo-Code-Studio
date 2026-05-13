"""MiMo API客户端 - 流式请求 + 工具调用"""

import json
import re
import threading
import traceback
import requests
from tools import TOOLS_DEFINITION, execute_tool


class MiMoClient:
    def __init__(self, config):
        self.config = config
        self.messages = []
        self._cancel = False
        self._busy = False
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}
        self.total_usage = {"input_tokens": 0, "output_tokens": 0}

    def clear_history(self):
        self.messages.clear()
        self.last_usage = {"input_tokens": 0, "output_tokens": 0}
        self.total_usage = {"input_tokens": 0, "output_tokens": 0}

    def cancel(self):
        self._cancel = True

    @property
    def is_busy(self):
        return self._busy

    def _parse_tool_calls(self, text: str) -> list:
        """从文本中解析工具调用（API未返回tool_use块时的回退方案）"""
        import re
        tool_uses = []

        # 匹配 <tool_calls>...</tool_calls> 格式
        tc_blocks = re.findall(r'<tool_calls>(.*?)</tool_calls>', text, re.DOTALL)
        for block in tc_blocks:
            # 匹配每个 <invoke>...</invoke>
            invokes = re.findall(r'<invoke>(.*?)</invoke>', block, re.DOTALL)
            for inv in invokes:
                name_m = re.search(r'<tool_name>(.*?)</tool_name>', inv)
                params_m = re.search(r'<parameters>(.*?)</parameters>', inv, re.DOTALL)
                if name_m:
                    name = name_m.group(1).strip()
                    params = {}
                    if params_m:
                        try:
                            params = json.loads(params_m.group(1).strip())
                        except json.JSONDecodeError:
                            pass
                    tool_uses.append({
                        "id": f"tool_{len(tool_uses)}",
                        "name": name,
                        "input": params,
                    })

        # 匹配 ```tool_name\n{...}\n``` 格式
        if not tool_uses:
            pattern = r'```(\w+)\s*\n(\{[\s\S]*?\})\s*\n```'
            for match in re.finditer(pattern, text):
                name = match.group(1)
                try:
                    params = json.loads(match.group(2))
                except json.JSONDecodeError:
                    continue
                tool_uses.append({
                    "id": f"tool_{len(tool_uses)}",
                    "name": name,
                    "input": params,
                })

        # 匹配 {"name":"xxx","arguments":{...}} 格式
        if not tool_uses:
            pattern2 = r'\{"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*(\{[\s\S]*?\})\}'
            for match in re.finditer(pattern2, text):
                name = match.group(1)
                try:
                    params = json.loads(match.group(2))
                except json.JSONDecodeError:
                    continue
                tool_uses.append({
                    "id": f"tool_{len(tool_uses)}",
                    "name": name,
                    "input": params,
                })

        return tool_uses

    def send_message(self, content: str, callbacks: dict):
        """
        发送消息并处理流式响应和工具调用
        callbacks:
            on_token(text) - 流式文本
            on_tool_start(name, params) - 工具开始执行
            on_tool_result(name, result) - 工具执行完成
            on_done(full_text) - 全部完成
            on_error(msg) - 错误
        """
        if self._busy:
            callbacks.get("on_error", lambda x: None)("上一条消息还在处理中，请稍候")
            return

        self._cancel = False
        self._busy = True
        self.messages.append({"role": "user", "content": content})

        on_error = callbacks.get("on_error", lambda x: None)

        def _worker():
            try:
                self._stream_loop(callbacks)
            except Exception as e:
                traceback.print_exc()
                if self.messages and self.messages[-1]["role"] == "user":
                    self.messages.pop()
                on_error(f"未知错误: {e}")
            finally:
                self._busy = False

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _stream_loop(self, callbacks: dict):
        """流式请求循环，处理工具调用"""
        on_token = callbacks.get("on_token", lambda x: None)
        on_tool_start = callbacks.get("on_tool_start", lambda n, p: None)
        on_tool_result = callbacks.get("on_tool_result", lambda n, r: None)
        on_done = callbacks.get("on_done", lambda x: None)
        on_error = callbacks.get("on_error", lambda x: None)

        max_iterations = 10  # 防止无限循环

        for iteration in range(max_iterations):
            if self._cancel:
                break

            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.config["api_key"],
                "anthropic-version": "2023-06-01",
            }
            body = {
                "model": self.config["model"],
                "max_tokens": self.config["max_tokens"],
                "stream": True,
                "messages": list(self.messages),
            }

            body["tools"] = TOOLS_DEFINITION

            system_prompt = self.config.get("system_prompt", "")
            wd = self.config.get("working_dir", "")
            if wd:
                system_prompt += f"\n\n当前工作目录: {wd}\n所有文件操作的相对路径都基于此目录。创建、读写、编辑文件时必须在此目录下进行。"
            system_prompt += (
                "\n\n工具使用规则："
                "\n- 当用户要求创建项目或指定文件结构时，必须按用户要求的文件结构分别创建每个文件，不要把所有代码合并到一个文件中"
                "\n- 例如用户说「创建 main.py、timer.py、ui.py」，就分别调用 write_file 创建这三个文件"
                "\n- 每个文件用独立的 write_file 调用，不要合并"
            )
            if system_prompt:
                body["system"] = system_prompt

            try:
                resp = requests.post(
                    self.config["api_url"],
                    headers=headers,
                    json=body,
                    stream=True,
                    timeout=120,
                )
                if resp.status_code != 200:
                    error_text = resp.text[:500]
                    on_error(f"API错误 ({resp.status_code}): {error_text}")
                    return
                resp.encoding = "utf-8"
            except requests.exceptions.ConnectionError as e:
                on_error(f"连接失败，请检查网络: {e}")
                return
            except requests.exceptions.Timeout as e:
                on_error(f"请求超时: {e}")
                return
            except requests.exceptions.RequestException as e:
                on_error(f"网络错误: {e}")
                return

            full_text = ""
            reasoning_content = ""
            content_blocks = []  # 保留完整内容块顺序（含 thinking/text/tool_use）
            current_block_type = None
            tool_uses = []
            current_tool = None
            current_tool_input = ""

            # 使用 iter_content 替代 iter_lines 以避免多字节字符截断
            buffer = ""
            done = False
            for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                if self._cancel or done:
                    break
                if not chunk:
                    continue
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        done = True
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type", "")

                    if event_type == "content_block_start":
                        block = event.get("content_block", {})
                        current_block_type = block.get("type", "")
                        if current_block_type == "tool_use":
                            current_tool = {
                                "id": block.get("id", ""),
                                "name": block.get("name", ""),
                                "input": "",
                            }
                            current_tool_input = ""
                        elif current_block_type == "thinking":
                            content_blocks.append({"type": "thinking", "thinking": ""})

                    elif event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        delta_type = delta.get("type", "")

                        if delta_type == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                full_text += text
                                on_token(text)

                        elif delta_type == "thinking_delta":
                            thinking_text = delta.get("thinking", "")
                            if thinking_text:
                                reasoning_content += thinking_text
                                if content_blocks and content_blocks[-1].get("type") == "thinking":
                                    content_blocks[-1]["thinking"] += thinking_text

                        elif delta_type == "input_json_delta":
                            current_tool_input += delta.get("partial_json", "")

                    elif event_type == "content_block_stop":
                        if current_tool is not None:
                            try:
                                current_tool["input"] = json.loads(current_tool_input) if current_tool_input else {}
                            except json.JSONDecodeError:
                                current_tool["input"] = {}
                            tool_uses.append(current_tool)
                            current_tool = None
                            current_tool_input = ""
                        current_block_type = None

                    elif event_type == "message_delta":
                        usage = event.get("usage", {})
                        if usage:
                            self.last_usage["output_tokens"] = usage.get("output_tokens", 0)
                        # 某些 API 在 message_delta 中返回 reasoning_content
                        delta_obj = event.get("delta", {})
                        if not reasoning_content:
                            reasoning_content = delta_obj.get("reasoning_content", "")

                    elif event_type == "message_start":
                        message = event.get("message", {})
                        usage = message.get("usage", {})
                        if usage:
                            self.last_usage["input_tokens"] = usage.get("input_tokens", 0)
                        # 某些 API 在 message 对象中返回 reasoning_content
                        if not reasoning_content:
                            reasoning_content = message.get("reasoning_content", "")

                    elif event_type == "message_stop":
                        done = True
                        break

            # 回退：从文本中解析工具调用
            if not tool_uses and full_text:
                tool_uses = self._parse_tool_calls(full_text)
                # 剥离原始标签文本，只保留自然语言部分
                if tool_uses:
                    full_text = re.sub(r'<tool_calls>[\s\S]*?</tool_calls>', '', full_text).strip()
                    full_text = re.sub(r'```tool_calls[\s\S]*?```', '', full_text).strip()

            # 如果有工具调用，执行它们
            if tool_uses:
                # 把AI的回复（包含tool_use）加入messages
                assistant_content = []
                # 保留 thinking 块（MiMo thinking 模式需要回传 reasoning_content）
                for blk in content_blocks:
                    if blk.get("type") == "thinking" and blk.get("thinking"):
                        assistant_content.append(blk)
                if full_text:
                    assistant_content.append({"type": "text", "text": full_text})
                for tu in tool_uses:
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tu["id"],
                        "name": tu["name"],
                        "input": tu["input"],
                    })
                assistant_msg = {"role": "assistant", "content": assistant_content}
                if reasoning_content:
                    assistant_msg["reasoning_content"] = reasoning_content
                self.messages.append(assistant_msg)

                # 执行工具并收集结果
                tool_results = []
                for tu in tool_uses:
                    if self._cancel:
                        break
                    name = tu["name"]
                    params = tu["input"]
                    on_tool_start(name, params)

                    wd = self.config.get("working_dir", "")
                    result = execute_tool(name, params, working_dir=wd)
                    on_tool_result(name, result)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tu["id"],
                        "content": result,
                    })

                self.messages.append({"role": "user", "content": tool_results})
                # 继续循环，让AI处理工具结果
                continue

            else:
                # 没有工具调用，完成
                if full_text:
                    assistant_msg = {"role": "assistant", "content": full_text}
                    if reasoning_content:
                        assistant_msg["reasoning_content"] = reasoning_content
                    self.messages.append(assistant_msg)
                on_done(full_text)
                return

        # 循环结束
        on_done(full_text)
