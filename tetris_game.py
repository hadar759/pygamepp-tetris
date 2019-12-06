from typing import Tuple, Optional, Dict

import pygame
from pygame import USEREVENT
from pygamepp.game import Game

from tetris_piece import Piece
from tetris_grid import TetrisGrid
from i_piece import IPiece
from colors import Colors
# TODO keep track of score (easy, but need to increase the screen size), and show it.
# TODO work on implementing 7 bag, and showing it. WORK ON WALL KICKS


class TetrisGame(Game):
    TEXT = pygame.font.Font("./resources/joystix-monospace.ttf", 60).render("YOU LOSE",
                                                                            True,
                                                                            Colors.WHITE)
    GRAVITY_EVENT = USEREVENT + 1
    DAS_EVENT = USEREVENT + 2
    ARR_EVENT = USEREVENT + 3
    MANUAL_DROP = USEREVENT + 4
    LOWER_BORDER = 19

    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int = 60,
                 background_path: Optional[str] = None):
        super().__init__(width, height, refresh_rate, background_path)
        self.cur_piece: Piece = None
        self.score = 42069
        self.grid = TetrisGrid()
        self.move_variables: Dict[str, bool] = {"right_das": False,
                                                "left_das": False,
                                                "arr": False,
                                                "key_down": False,
                                                "hard_drop": False,
                                                "manual_drop": False}

    def run(self):
        self.cur_piece = IPiece()
        # Every event that has to do with moving the piece
        self.create_timer(self.GRAVITY_EVENT, 500)
        self.set_event_handler(self.GRAVITY_EVENT, self.gravitate)
        self.create_timer(self.MANUAL_DROP, 20)
        self.set_event_handler(self.MANUAL_DROP, self.manual_drop)
        self.set_event_handler(self.DAS_EVENT, self.start_DAS)
        self.set_event_handler(self.ARR_EVENT, self.start_ARR)
        self.set_event_handler(pygame.KEYUP, self.key_up)
        self.set_event_handler(pygame.KEYDOWN, self.key_pressed)
        self.running = True
        self.cur_piece = None

        self.grid.display_borders(self.screen)
        super().run()

    def start_of_loop(self):
        if self.cur_piece is None:
            for key in self.move_variables:
                self.move_variables[key] = False
            self.cur_piece = IPiece()
            self.game_objects.append(self.cur_piece)

    def end_of_loop(self):
        if self.cur_piece:
            self.should_freeze_piece()
        self.clear_lines()

    def hard_drop(self):
        while self.cur_piece is not None:
            self.gravitate()
            self.should_freeze_piece()

    def gravitate(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.gravitate(self.grid)

    def manual_drop(self):
        if self.move_variables["manual_drop"]:
            self.gravitate()

    def key_down(self):
        self.move_variables["manual_drop"] = True

    def key_pressed(self, event: pygame.event.EventType):
        if event.key == pygame.K_SPACE:
            self.hard_drop()
        elif event.key == pygame.K_DOWN:
            self.key_down()
        elif event.key == pygame.K_RIGHT:
            self.key_right()
        elif event.key == pygame.K_LEFT:
            self.key_left()
        elif event.key == pygame.K_z:
            self.key_z()
        elif event.key == pygame.K_x:
            self.key_x()

    def key_up(self):
        if self.last_pressed_key == pygame.K_DOWN:
            self.move_variables["manual_drop"] = False
        elif self.last_pressed_key in [pygame.K_RIGHT, pygame.K_LEFT]:
            for key in self.move_variables:
                self.move_variables[key] = False

    def start_ARR(self):
        if self.move_variables["key_down"]:
            self.move_variables["arr"] = True
            self.create_timer(self.DAS_EVENT, 30, True)

    def start_DAS(self):
        if self.move_variables["arr"]:
            if self.move_variables["right_das"]:
                self.grid.reset_screen(self.screen)
                self.cur_piece.move(pygame.K_RIGHT, self.grid)
                self.create_timer(self.DAS_EVENT, 30, True)
            elif self.move_variables["left_das"]:
                self.grid.reset_screen(self.screen)
                self.cur_piece.move(pygame.K_LEFT, self.grid)
                self.create_timer(self.DAS_EVENT, 30, True)
    
    def key_right(self):
        self.grid.reset_screen(self.screen)
        pygame.time.set_timer(self.ARR_EVENT, 100, True)
        self.move_variables["key_down"] = True
        self.move_variables["right_das"] = True
        self.cur_piece.move(pygame.K_RIGHT, self.grid)
        
    def key_left(self):
        self.grid.reset_screen(self.screen)
        pygame.time.set_timer(self.ARR_EVENT, 140, True)
        self.move_variables["key_down"] = True
        self.move_variables["left_das"] = True
        self.cur_piece.move(pygame.K_LEFT, self.grid)

    def key_z(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.rotate(pygame.K_z, self.grid)

    def key_x(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.rotate(pygame.K_x, self.grid)

    def should_freeze_piece(self):
        for pos in self.cur_piece.position:
            if pos[0] >= self.LOWER_BORDER:
                self.grid.freeze_piece(self.cur_piece)
                self.cur_piece = None
                break

            elif self.grid.blocks[pos[0] + 1][pos[1]].occupied:
                self.grid.freeze_piece(self.cur_piece)
                if pos[0] <= 0:
                    self.game_over()
                self.cur_piece = None
                break

    def game_over(self):
        pygame.time.wait(1000)
        self.fade(7)
        self.screen.blit(self.TEXT, self.calculate_center_name_position())
        pygame.display.flip()

        pygame.time.wait(2500)
        self.fade(7)
        self.running = False
        self.background_image = pygame.image.load("./resources/end-screen.png")
        self.screen = pygame.display.set_mode((self.background_image.get_size()[0],
                                               self.background_image.get_size()[1]))
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.render_score(), (600, 75))
        pygame.display.flip()
        pygame.time.wait(5000)

    def render_score(self):
        return pygame.font.Font("./resources/joystix-monospace.ttf", 50).render(str(self.score),
                                                                                True,
                                                                                Colors.WHITE)

    def fade(self, delay):
        fade = pygame.Surface((self.screen.get_rect()[2], self.screen.get_rect()[3]))
        fade.fill((0, 0, 0))
        for alpha in range(0, 100):
            fade.set_alpha(alpha)
            self.screen.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(delay)

    def calculate_center_name_position(self) -> Tuple[int, int]:
        """Returns the center position the text should be in"""
        return (max(0, self.screen.get_rect()[2] // 2 - self.TEXT.get_rect()[2] // 2),
                max(0, self.screen.get_rect()[3] // 2 - self.TEXT.get_rect()[3] // 2))

    def clear_lines(self):
        for index, line in enumerate(self.grid.blocks):
            should_clear = True
            for block in line:
                if not block.occupied:
                    should_clear = False
            if should_clear:
                self.clear_line(index)

    def clear_line(self, line_num):
        for piece in self.game_objects:
            new_pos = []
            for pos in piece.position:
                self.grid.blocks[pos[0]][pos[1]].occupied = False
                if pos[0] != line_num:
                    if pos[0] < line_num:
                        pos[0] += 1
                    new_pos.append(pos)
            piece.position = new_pos
            for pos in piece.position:
                self.grid.occupy_block(pos)
