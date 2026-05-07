"""MiMo Code Studio - 入口文件"""

from config import Config
from api_client import MiMoClient
from audio_player import AudioPlayer
from ui.app import App


def main():
    config = Config()
    api = MiMoClient(config)
    player = AudioPlayer()

    app = App(config, api, player)
    app.mainloop()


if __name__ == "__main__":
    main()
