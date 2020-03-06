import copy
from typing import Tuple, Optional, Dict
import random

import pygame
from pygame import USEREVENT
from pygamepp.game import Game

from pieces import *
from pieces.tetris_piece import Piece
from tetris_grid import TetrisGrid
from colors import Colors
.
# TODO if i want: make the ghost piece more ghost-y (less opacity) + i dunno think of more features


class TetrisGame(Game):
    LOSE_TEXT = pygame.font.Font("./resources/joystix-monospace.ttf", 60).render("YOU LOSE",
                                                                                 True,
                                                                                 Colors.WHITE)
    WIN_TEXT = pygame.font.Font("./resources/joystix-monospace.ttf", 60).render("YOU WIN",
                                                                                 True,
                                                                                 Colors.WHITE)
    SCORE_TEXT = pygame.font.Font("./resources/joystix-monospace.ttf", 19).render("SCORE:",
                                                                                  True,
                                                                                  Colors.WHITE)
    TIME_TEXT = pygame.font.Font("./resources/joystix-monospace.ttf", 19).render("TIME:",
                                                                                  True,
                                                                                  Colors.WHITE)
    GRAVITY_EVENT = USEREVENT + 1
    DAS_EVENT = USEREVENT + 2
    ARR_EVENT = USEREVENT + 3
    MANUAL_DROP = USEREVENT + 4
    LOCK_DELAY = USEREVENT + 5
    LOWER_BORDER = 19
    GRAVITY_BASE_TIME = 800
    PIECES_AND_NEXT_SPRITES = {"<class 'pieces.i_piece.IPiece'>": pygame.image.load("./resources/ipiece-full-sprite.png"),
                               "<class 'pieces.j_piece.JPiece'>": pygame.image.load("./resources/jpiece-full-sprite.png"),
                               "<class 'pieces.o_piece.OPiece'>": pygame.image.load("./resources/opiece-full-sprite.png"),
                               "<class 'pieces.l_piece.LPiece'>": pygame.image.load("./resources/lpiece-full-sprite.png"),
                               "<class 'pieces.t_piece.TPiece'>": pygame.image.load("./resources/tpiece-full-sprite.png"),
                               "<class 'pieces.s_piece.SPiece'>": pygame.image.load("./resources/spiece-full-sprite.png"),
                               "<class 'pieces.z_piece.ZPiece'>": pygame.image.load("./resources/zpiece-full-sprite.png")}

    def __init__(self,
                 width: int,
                 height: int,
                 mode: str,
                 refresh_rate: int = 60,
                 background_path: Optional[str] = None,
                 lines_or_level: Optional[int] = None):
        super().__init__(width, height, refresh_rate, background_path)
        self.mode = mode
        self.cur_piece: Piece = None
        self.ghost_piece: Piece = None
        self.lines_cleared = 0
        self.level = 0
        self.score = 0
        self.temp_freeze = False
        self.cur_seven_bag = []
        self.grid = TetrisGrid()
        self.move_variables: Dict[str, bool] = {"right_das": False,
                                                "left_das": False,
                                                "arr": False,
                                                "key_down": False,
                                                "hard_drop": False,
                                                "manual_drop": False}
        if self.mode == "sprint":
            self.starting_time = pygame.time.get_ticks()
            self.lines_to_finish = lines_or_level
            self.line_text = pygame.font.Font("./resources/joystix-monospace.ttf", 19).render("LEFT:",
                                                                                         True,
                                                                                         Colors.WHITE)
        self.gravity_time = self.GRAVITY_BASE_TIME
        if self.mode == "marathon":
            self.level = lines_or_level
            self.gravity_time -= self.level * 83
            self.line_text = pygame.font.Font("./resources/joystix-monospace.ttf", 19).render("LINES:",
                                                                                         True,
                                                                                         Colors.WHITE)
        self.freeze_thingy_rename = 0

    def run(self):
        # Every event that has to do with moving the piece
        if self.mode != "sprint":
            self.create_timer(self.GRAVITY_EVENT, self.gravity_time)
        self.set_event_handler(self.GRAVITY_EVENT, self.gravitate)
        self.create_timer(self.MANUAL_DROP, 20)
        self.set_event_handler(self.MANUAL_DROP, self.manual_drop)
        self.set_event_handler(self.DAS_EVENT, self.start_DAS)
        self.set_event_handler(self.ARR_EVENT, self.start_ARR)
        self.set_event_handler(self.LOCK_DELAY, self.freeze_piece)
        self.set_event_handler(pygame.KEYUP, self.key_up)
        self.set_event_handler(pygame.KEYDOWN, self.key_pressed)
        self.running = True

        self.grid.display_borders(self.screen)
        super().run()

    def start_of_loop(self):
        if self.cur_piece is None:
            self.generate_new_piece()

    def show_next_pieces(self):
        step = 200
        for i in range(5):
            cur_next_piece = self.cur_seven_bag[i]
            self.screen.blit(self.PIECES_AND_NEXT_SPRITES[str(cur_next_piece)], (500, 100 + step * i))

    def initialize_ghost_piece(self):
        if self.ghost_piece in self.game_objects:
            self.game_objects.remove(self.ghost_piece)

        self.ghost_piece = type(self.cur_piece)()
        self.ghost_piece.sprite.set_alpha(255)
        self.update_ghost_position()
        self.game_objects.append(self.ghost_piece)

    def update_ghost_position(self):
        if self.cur_piece:
            self.ghost_piece.position = self.cur_piece.get_lowest_position(self.grid)

    def end_of_loop(self):
        if self.cur_piece:
            self.temp_freeze = self.should_freeze_piece()
        if self.mode == "marathon":
            self.marathon()
            self.show_score()
            self.show_lines()
        elif self.mode == "sprint":
            self.show_time()
            self.show_lines()
        self.clear_lines()
        self.show_next_pieces()
        if self.mode == "sprint" and self.lines_cleared >= self.lines_to_finish:
            self.game_over(True)

    def marathon(self):
        total_time_decrease = 0
        for i in range(self.level):
            if i < 9:
                total_time_decrease += 83
            if i == 9:
                total_time_decrease += 33
            if 9 < i < 29:
                total_time_decrease += 17

        temp_gravity_time = (self.GRAVITY_BASE_TIME - total_time_decrease)

        if self.gravity_time != temp_gravity_time:
            self.gravity_time = temp_gravity_time
            self.create_timer(self.GRAVITY_EVENT, self.gravity_time)

    def generate_new_piece(self):
        for key in self.move_variables:
            self.move_variables[key] = False
        self.generate_seven_bag()
        self.cur_piece = self.cur_seven_bag.pop(0)()
        self.game_objects.append(self.cur_piece)
        self.initialize_ghost_piece()

    def generate_seven_bag(self):
        seven_piece_set = [IPiece, TPiece, ZPiece, SPiece, LPiece, JPiece, OPiece]
        if self.cur_seven_bag.count(SPiece) == 2:
            seven_piece_set.remove(SPiece)
        if self.cur_seven_bag.count(ZPiece) == 2:
            seven_piece_set.remove(ZPiece)

        while len(self.cur_seven_bag) < 7:
            self.cur_seven_bag.append(random.choice(seven_piece_set))

    def get_current_time_since_start(self):
        return (pygame.time.get_ticks() - self.starting_time) // 1000

    def show_score(self):
        text = self.render_input(20, str(self.score))
        self.screen.blit(self.SCORE_TEXT, (500, 10))
        self.screen.blit(text, (500 + self.SCORE_TEXT.get_rect()[2], 10))

    def show_time(self):
        seconds = self.render_input(20, str(self.get_current_time_since_start()))
        self.screen.fill(0x000000, [(500 + self.line_text.get_rect()[2], 10), (500 + self.line_text.get_rect()[2] + 300, 40)])
        self.screen.blit(self.TIME_TEXT, (500, 10))
        self.screen.blit(seconds, (500 + self.line_text.get_rect()[2], 10))

    def show_lines(self):
        lines = self.lines_cleared
        if self.mode == "sprint":
            lines = self.lines_to_finish - lines
        text = self.render_input(20, str(lines))
        self.screen.blit(self.line_text, (500, 50))
        self.screen.blit(text, (500 + self.line_text.get_rect()[2], 50))

    def hard_drop(self):
        if self.temp_freeze:
            self.freeze_piece()
            return
        drop = True
        while drop:
            self.gravitate()
            self.score += 2
            if self.should_freeze_piece():
                self.freeze_piece()
                drop = False
        self.clear_lines()

    def gravitate(self):
        if not self.temp_freeze and self.cur_piece:
            self.grid.reset_screen(self.screen)
            self.cur_piece.gravitate(self.grid)
        else:
            if self.freeze_thingy_rename > 0:
                self.freeze_piece()
                self.temp_freeze = False
                self.freeze_thingy_rename = 0
            else:
                self.freeze_thingy_rename += 1

    def manual_drop(self):
        if self.move_variables["manual_drop"]:
            self.score += 1
            if not self.temp_freeze:
                self.gravitate()

    def key_down(self):
        self.move_variables["manual_drop"] = True

    def key_pressed(self, event: pygame.event.EventType):
        if event.key == pygame.K_SPACE:
            self.hard_drop()

        elif self.cur_piece:
            if event.key == pygame.K_DOWN:
                self.key_down()
            elif event.key == pygame.K_RIGHT:
                self.key_right()
            elif event.key == pygame.K_LEFT:
                self.key_left()
            elif event.key == pygame.K_z:
                self.key_z()
            elif event.key == pygame.K_x:
                self.key_x()
            self.update_ghost_position()

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
        if self.move_variables["arr"] and self.cur_piece:
            if self.move_variables["right_das"]:
                self.grid.reset_screen(self.screen)
                self.cur_piece.move(pygame.K_RIGHT, self.grid)
                self.create_timer(self.DAS_EVENT, 30, True)
            elif self.move_variables["left_das"]:
                self.grid.reset_screen(self.screen)
                self.cur_piece.move(pygame.K_LEFT, self.grid)
                self.create_timer(self.DAS_EVENT, 30, True)
        self.update_ghost_position()

    def key_right(self):
        self.grid.reset_screen(self.screen)
        self.create_timer(self.ARR_EVENT, 100, True)
        self.move_variables["key_down"] = True
        self.move_variables["right_das"] = True
        self.cur_piece.move(pygame.K_RIGHT, self.grid)

    def key_left(self):
        self.grid.reset_screen(self.screen)
        self.create_timer(self.ARR_EVENT, 100, True)
        self.move_variables["key_down"] = True
        self.move_variables["left_das"] = True
        self.cur_piece.move(pygame.K_LEFT, self.grid)

    def key_z(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.call_rotation_functions(pygame.K_z, self.grid)

    def key_x(self):
        self.grid.reset_screen(self.screen)
        self.cur_piece.call_rotation_functions(pygame.K_x, self.grid)

    def start_lock_delay(self):
        if self.should_freeze_piece():
            self.create_timer(self.LOCK_DELAY, self.gravity_time * 2, True)

    def freeze_piece(self):
        self.grid.freeze_piece(self.cur_piece)
        self.cur_piece = None
        self.temp_freeze = False

    def should_freeze_piece(self):
        for pos in self.cur_piece.position:
            if pos[0] >= self.LOWER_BORDER:
                return True

            elif self.grid.blocks[pos[0] + 1][pos[1]].occupied:
                if pos[0] <= 0:
                    self.game_over(False)
                return True
        return False

    def game_over(self, win: bool):
        if self.mode == "sprint":
            final_time = self.get_current_time_since_start()
        pygame.time.wait(1000)
        self.fade(7)
        if self.mode == "sprint" and win:
            self.screen.blit(self.WIN_TEXT, self.calculate_center_name_position(
                self.screen.get_rect()[2] // 2 - self.WIN_TEXT.get_rect()[2] // 2,
                self.screen.get_rect()[3] // 2 - self.WIN_TEXT.get_rect()[3] // 2))
        else:
            self.screen.blit(self.LOSE_TEXT, self.calculate_center_name_position(
                self.screen.get_rect()[2] // 2 - self.LOSE_TEXT.get_rect()[2] // 2,
                self.screen.get_rect()[3] // 2 - self.LOSE_TEXT.get_rect()[3] // 2))
        pygame.display.flip()

        pygame.time.wait(2500)
        self.fade(7)
        self.running = False
        self.background_image = pygame.image.load("./resources/end-screen.png")
        self.screen = pygame.display.set_mode((self.background_image.get_size()[0],
                                               self.background_image.get_size()[1]))
        self.screen.blit(self.background_image, (0, 0))
        if self.mode == "marathon":
            self.screen.blit(self.render_input(50, "SCORE:"), (300, 75))
            self.screen.blit(self.render_input(50, str(self.score)), (550, 75))
        elif self.mode == "sprint":
            rendered_time_text = self.render_input(50, "TIME:")
            self.screen.blit(rendered_time_text, (300, 75))
            rendered_time = self.render_input(50, str(final_time))
            self.screen.blit(rendered_time, (515, 75))
            self.screen.blit(self.render_input(50, "Seconds"), (530 + rendered_time.get_rect()[2], 75))
        pygame.display.flip()
        pygame.time.wait(5000)

    def render_input(self, font_size: int, inp):
        return pygame.font.Font("./resources/joystix-monospace.ttf", font_size).render(
            inp,
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

    def calculate_center_name_position(self, x_space: int, y_space: int) -> Tuple[int, int]:
        """Returns the center position the text should be in"""
        return max(0, x_space), max(0, y_space)

    def clear_lines(self):
        num_of_lines_cleared = 0
        for index, line in enumerate(self.grid.blocks):
            should_clear = True
            for block in line:
                if not block.occupied:
                    should_clear = False
            if should_clear:
                num_of_lines_cleared += 1
                self.clear_line(index)

        if num_of_lines_cleared != 0:
            self.grid.reset_screen(self.screen)

        if self.lines_cleared // 10 < (self.lines_cleared + num_of_lines_cleared) // 10:
            self.level += 1

        self.lines_cleared += num_of_lines_cleared
        if num_of_lines_cleared == 1:
            self.score += 40 * (self.level + 1)
        elif num_of_lines_cleared == 2:
            self.score += 100 * (self.level + 1)
        elif num_of_lines_cleared == 3:
            self.score += 300 * (self.level + 1)
        elif num_of_lines_cleared == 4:
            self.score += 1200 * (self.level + 1)

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
