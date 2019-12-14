import pygame

from pieces.tetris_piece import Piece


class IPiece(Piece):
    PIVOT_POINT = 1

    def __init__(self):
        self.sprite = pygame.image.load(r"./resources/ipiece-sprite.png")
        super().__init__(self.sprite, [[0, 4], [1, 4], [2, 4], [3, 4]])

    def rotate_clockwise(self, grid):
        illegal_rotation = False
        old_positions = self.position[:]
        pivot_point = self.position[self.PIVOT_POINT]
        for i in range(len(self.position)):
            self.position[i] = self.rotated_piece_position(self.position[i],
                                                           pivot_point,
                                                           self.CLOCKWISE_TRANSFORMATION_MATRIX)
            if (self.position[i][1] < self.LEFT_BORDER
                    or self.position[i][1] > self.RIGHT_BORDER
                    or self.position[i][0] > self.LOWER_BORDER
                    or grid.blocks[self.position[i][0]][self.position[i][1]].occupied):
                illegal_rotation = True
        if illegal_rotation:
            self.position = old_positions

    def rotate_counter_clockwise(self, grid):
        illegal_rotation = False
        old_positions = self.position[:]
        pivot_point = self.position[self.PIVOT_POINT]
        for i in range(len(self.position)):
            self.position[i] = self.rotated_piece_position(self.position[i],
                                                           pivot_point,
                                                           self.COUNTER_CLOCKWISE_TRANSFORMATION_MATRIX)
            if (self.position[i][1] < self.LEFT_BORDER
                    or self.position[i][1] > self.RIGHT_BORDER
                    or self.position[i][0] > self.LOWER_BORDER
                    or grid.blocks[self.position[i][0]][self.position[i][1]].occupied):
                illegal_rotation = True
        if illegal_rotation:
            self.position = old_positions
