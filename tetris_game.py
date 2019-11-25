from typing import List, Optional, Dict

import pygame
from pygame import USEREVENT
from pygamepp.game import Game

from tetris_piece import Piece
from tetris_grid import TetrisGrid
from i_piece import IPiece

# TODO work on clearing lines, make manual drop stop and find a fix for manual drop falling too far.


class TetrisGame(Game):
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
        self.frozen_pieces: List[Piece] = []
        self.cur_piece: Piece = None
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
        self.create_timer(self.MANUAL_DROP, 50)
        self.set_event_handler(self.MANUAL_DROP, self.manual_drop)
        self.set_event_handler(self.DAS_EVENT, self.start_DAS)
        self.set_event_handler(self.ARR_EVENT, self.start_ARR)
        self.set_event_handler(pygame.K_SPACE, self.key_space)
        self.set_event_handler(pygame.KEYUP, self.key_up)
        self.set_event_handler(pygame.K_DOWN, self.key_down)
        self.set_event_handler(pygame.K_RIGHT, self.key_right)
        self.set_event_handler(pygame.K_LEFT, self.key_left)
        self.set_event_handler(pygame.K_z, self.key_z)
        self.set_event_handler(pygame.K_x, self.key_x)
        self.running = True
        self.cur_piece = None

        while self.running:
            self.grid.display_borders(self.screen)
            if self.cur_piece is None:
                for key in self.move_variables:
                    self.move_variables[key] = False
                self.cur_piece = IPiece()
                self.game_objects.append(self.cur_piece)

            super().run()
            self.should_freeze_piece()
            self.clear_lines()

    def gravitate(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.gravitate()

    def manual_drop(self):
        if self.move_variables["manual_drop"]:
            self.gravitate()

    def key_down(self):
        self.move_variables["manual_drop"] = True

    def key_up(self):
        for key in self.move_variables:
            if key != "manual_drop":
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

    def key_space(self):
        self.move_variables["hard_drop"] = True

    def hard_drop(self):
        if self.move_variables["hard_drop"]:
            self.gravitate()

    def should_freeze_piece(self):
        for pos in self.cur_piece.position:
            if pos[0] == self.LOWER_BORDER:
                self.grid.freeze_piece(self.cur_piece)
                self.cur_piece = None
                break

            elif self.grid.blocks[pos[0] + 1][pos[1]].occupied:
                self.grid.freeze_piece(self.cur_piece)
                self.cur_piece = None
                break

    def clear_lines(self):
        pass
