import pygame
from pygamepp.grid import Grid

from colors import Colors
from tetris_piece import Piece


class TetrisGrid(Grid):
    def __init__(self):
        super().__init__(20, 10, 50)

    def display_borders(self, screen: pygame.Surface):
        block_size = 50
        for row in self.blocks:
            for block in row:
                block_proportions = block.position
                pygame.draw.line(screen, Colors.GREY,
                                 block_proportions, (block_proportions[0] + 10,
                                                     block_proportions[1]))
                pygame.draw.line(screen, Colors.DARK_GREY,
                                 (block_proportions[0] + 10, block_proportions[1]),
                                 (block_proportions[0] + block_size - 10, block_proportions[1]))
                pygame.draw.line(screen, Colors.GREY,
                                 block_proportions, (block_proportions[0],
                                                     block_proportions[1] + 10))
                pygame.draw.line(screen, Colors.DARK_GREY,
                                 (block_proportions[0], block_proportions[1] + 10),
                                 (block_proportions[0], block_proportions[1] + block_size - 10))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0] + block_size, block_proportions[1]),
                                 (block_proportions[0] + block_size - 10, block_proportions[1]))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0] + block_size, block_proportions[1]),
                                 (block_proportions[0] + block_size, block_proportions[1] + 10))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0] + block_size,
                                  block_proportions[1] + block_size)
                                 , (block_proportions[0] + block_size - 10,
                                    block_proportions[1] + block_size))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0] + block_size,
                                  block_proportions[1] + block_size),
                                 (block_proportions[0] + block_size,
                                  block_proportions[1] + block_size - 10))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0], block_proportions[1] + block_size),
                                 (block_proportions[0] + 10, block_proportions[1] + block_size))
                pygame.draw.line(screen, Colors.GREY,
                                 (block_proportions[0], block_proportions[1] + block_size),
                                 (block_proportions[0], block_proportions[1] + block_size - 10))
                pygame.draw.line(screen, Colors.DARK_GREY,
                                 (block_proportions[0] + 10, block_proportions[1] + block_size),
                                 (block_proportions[0] + block_size - 10,
                                  block_proportions[1] + block_size))

    def reset_screen(self, screen: pygame.Surface):
        screen.fill(Colors.BLACK)
        self.display_borders(screen)


    def freeze_piece(self, piece: Piece):
        for pos in piece.position:
            print(pos[0], pos[1])
            self.blocks[pos[0]][pos[1]].occupied = True
