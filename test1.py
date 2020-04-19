import tetris_game
from tetris_server import TetrisServer


def main():
    server_game = tetris_game.TetrisGame(500 + 200, 1000, "multiplayer", 75)
    server = TetrisServer(server_game)
    server.run()


if __name__ == "__main__":
    main()
