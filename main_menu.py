from typing import Optional, Tuple

import pygame

import tetris_game
from button import Button
from colors import Colors
from tetris_client import TetrisClient
from tetris_server import TetrisServer


class MainMenu:
    BUTTON_PRESS = pygame.MOUSEBUTTONDOWN

    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int = 60,
                 background_path: Optional[str] = None):
        self.width, self.height = width, height
        self.refresh_rate = refresh_rate
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background_image = pygame.image.load(background_path) if background_path else None
        self.buttons = []

    def run(self):
        self.screen.blit(self.background_image, (0, 0))
        # Very specific numbers just so they exactly fill the blocks in the background pic hahaha
        self.create_button((self.width // 2 - 258, self.height // 3 - 250), 504, 200, Colors.BLACK, "sprint")
        self.create_button((self.width // 2 - 258, self.height // 3 * 2 - 250), 504, 200, Colors.BLACK, "marathon")
        self.create_button((self.width // 2 - 258, self.height - 250), 504, 200, Colors.BLACK, "multiplayer")
        self.show_buttons()
        self.show_text_in_buttons()
        pygame.display.flip()
        run = True
        while run:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == self.BUTTON_PRESS:
                    for button in self.buttons:
                        if button.inside_button(mouse_pos):
                            if button.text == "sprint":
                                self.sprint()
                            elif button.text == "marathon":
                                self.marathon()
                            elif button.text == "multiplayer":
                                self.multiplayer()
                            elif button.text[-1] == "L":
                                self.start_game("sprint", button.text[:2])
                            elif button.text == "SERVER":
                                self.start_multiplayer(True)
                            elif button.text == "CLIENT":
                                self.start_multiplayer(False)
                            else:
                                self.start_game("marathon", button.text)

    def multiplayer(self):
        self.buttons = []
        self.screen.blit(self.background_image, (0, 0))
        self.create_button((self.width // 3 - 300, self.height // 2 - 100), 500, 200, Colors.BLACK, "SERVER")
        self.create_button(((self.width // 3) * 2 - 200, self.height // 2 - 100), 500, 200, Colors.BLACK, "CLIENT")
        self.show_buttons()
        self.show_text_in_buttons()
        pygame.display.flip()

    def sprint(self):
        self.buttons = []
        self.screen.blit(self.background_image, (0, 0))
        self.create_button((self.width // 2 - 257, self.height // 8 - 85), 501, 200, Colors.BLACK, "20L")
        self.create_button((self.width // 2 - 257, self.height // 8 * 3 - 81), 501, 200, Colors.BLACK, "40L")
        self.create_button((self.width // 2 - 257, self.height // 8 * 5 - 86), 501, 200, Colors.BLACK, "100L")
        self.create_button((self.width // 2 - 257, self.height // 8 * 7 - 85), 501, 200, Colors.BLACK, "1000L")
        self.show_buttons()
        self.show_text_in_buttons()
        pygame.display.flip()

    def marathon(self):
        self.buttons = []
        self.screen.blit(self.background_image, (0, 0))
        button_height = 200
        button_width = 200
        row_height = self.height // 2 - button_height
        row_starting_width = self.width // 10
        # First Line
        for i in range(5):
            self.create_button((row_starting_width * (3 + (i - 1) * 2) - 100, row_height),
                               button_width,
                               button_height,
                               Colors.BLACK,
                               str(i))
        # Second Line
        row_height = row_height + button_height + 100
        for i in range(5):
            self.create_button((row_starting_width * (3 + (i - 1) * 2) - 100, row_height),
                               button_width,
                               button_height,
                               Colors.BLACK,
                               str(i + 5))
        self.show_buttons()
        self.show_text_in_buttons()
        pygame.display.flip()

    def start_multiplayer(self, host: bool):
        if host:
            server_game = tetris_game.TetrisGame(500 + 200, 1000, "multiplayer", 75)
            server = TetrisServer(server_game)
            server.run()
        else:
            client_game = tetris_game.TetrisGame(500 + 200, 1000, "multiplayer", 75)
            client = TetrisClient(client_game)
            client.run()

    @staticmethod
    def start_game(mode, lines_or_level):
        game = tetris_game.TetrisGame(500 + 200, 1000, mode, 75, lines_or_level=int(lines_or_level))
        game.run()

    def create_button(self, starting_pixel: Tuple[int, int], width: int, height: int, color: int, text: str):
        self.buttons.append(Button(starting_pixel, width, height, color, text))

    def show_buttons(self):
        for button in self.buttons:
            x = button.starting_x
            y = button.starting_y
            self.screen.fill(button.color, ((x, y), (button.width, button.height)))

    def show_text_in_buttons(self):
        for button in self.buttons:
            self.screen.blit(button.rendered_text, button.get_text_position())
