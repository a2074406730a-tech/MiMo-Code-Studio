"""音频播放模块 - pygame"""

import threading
import traceback
import pygame
from tts_engine import generate_audio_sync, cleanup_audio


class AudioPlayer:
    def __init__(self):
        self._init_mixer()
        self._playing = False
        self._stop_flag = False
        self._current_file = None

    def _init_mixer(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

    @property
    def is_playing(self) -> bool:
        return self._playing

    def stop(self):
        self._stop_flag = True
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._playing = False

    def speak(self, text: str, voice: str, rate: int, volume: int,
              on_start=None, on_end=None):
        """朗读文本"""
        self.stop()
        self._stop_flag = False

        def _worker():
            tmp_path = None
            try:
                tmp_path = generate_audio_sync(text, voice, rate, volume)
                self._current_file = tmp_path

                if self._stop_flag:
                    cleanup_audio(tmp_path)
                    return

                # 每次播放前重新初始化mixer，防止长时间运行后失效
                try:
                    self._init_mixer()
                except Exception:
                    pass

                self._playing = True
                if on_start:
                    on_start()

                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    if self._stop_flag:
                        pygame.mixer.music.stop()
                        break
                    pygame.time.wait(100)

                self._playing = False
                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

                if on_end:
                    on_end()

            except Exception as e:
                self._playing = False
                traceback.print_exc()
                if on_end:
                    on_end()
            finally:
                if tmp_path:
                    cleanup_audio(tmp_path)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
