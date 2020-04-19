import tetris_game
from tetris_client import TetrisClient


def main():
    client_game = tetris_game.TetrisGame(500 + 200, 1000, "multiplayer", 75)
    client = TetrisClient(client_game)
    client.run()


if __name__ == "__main__":
    main()
