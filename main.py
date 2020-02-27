import ctypes

import tetris_game


def main():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    game = tetris_game.TetrisGame(500 + 200, 1000, "sprint", 75)
    game.run()


if __name__ == "__main__":
    main()
