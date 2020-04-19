import socket
from tetris_game import TetrisGame


class TetrisClient:
    HOST_IP = "192.168.1.18"
    DST_PORT = 4000

    def __init__(self, tetris_game: TetrisGame):
        self.client_socket = socket.socket()
        self.tetris_game = tetris_game

    def connect_to_server(self):
        """Connects the socket to a server"""
        self.client_socket.connect((self.HOST_IP, self.DST_PORT))

    def run(self):
        self.connect_to_server()
        self.client_socket.send(str(0).encode())
        self.tetris_game.client_socket = self.client_socket
        self.tetris_game.run()
