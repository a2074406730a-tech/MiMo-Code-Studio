"""语音合成模块 - edge-tts"""

import asyncio
import os
import uuid

import edge_tts

VOICE_LIST = [
    ("zh-CN-XiaoxiaoNeural", "晓晓（女声，温柔）"),
    ("zh-CN-XiaoxiaoMultilingualNeural", "晓晓多语言（女声）"),
    ("zh-CN-YunxiNeural", "云希（男声，阳光）"),
    ("zh-CN-YunjianNeural", "云健（男声，沉稳）"),
    ("zh-CN-XiaoyiNeural", "晓艺（女声，活泼）"),
]


async def _generate_audio(text: str, voice: str, rate: int, volume: int) -> str:
    """生成音频文件，返回临时文件路径"""
    import tempfile
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"mimo_tts_{uuid.uuid4().hex[:8]}.mp3")

    rate_str = f"+{rate}%" if rate >= 0 else f"{rate}%"
    vol_adjust = volume - 80
    vol_str = f"+{vol_adjust}%" if vol_adjust >= 0 else f"{vol_adjust}%"

    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate_str, volume=vol_str)
    await comm.save(tmp_path)
    return tmp_path


def generate_audio_sync(text: str, voice: str, rate: int, volume: int) -> str:
    """同步版本的音频生成，失败自动重试，最终回退到备选语音"""
    import time
    fallback_voice = "zh-CN-XiaoxiaoNeural"
    voices_to_try = [voice]
    if voice != fallback_voice:
        voices_to_try.append(fallback_voice)

    last_error = None
    for v in voices_to_try:
        for attempt in range(2):
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(_generate_audio(text, v, rate, volume))
                return result
            except Exception as e:
                last_error = e
                try:
                    loop.close()
                except Exception:
                    pass
                if attempt < 1:
                    time.sleep(1)
                    continue
            finally:
                if not loop.is_closed():
                    try:
                        loop.close()
                    except Exception:
                        pass
    raise last_error


def cleanup_audio(path: str):
    """清理临时音频文件"""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except Exception:
        pass
