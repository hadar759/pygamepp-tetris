from typing import List, Tuple

import pygame
from pygamepp.grid_game_object import GridGameObject
from pygamepp.grid import Grid


class Piece(GridGameObject):
    COUNTER_CLOCKWISE_TRANSFORMATION_MATRIX = ((0, -1), (1, 0))
    CLOCKWISE_TRANSFORMATION_MATRIX = ((0, 1), (-1, 0))
    RIGHT_BORDER = 9
    LEFT_BORDER = 0
    LOWER_BORDER = 19

    def __init__(self, sprite: pygame.sprite, position: List):
        super().__init__(sprite, position, 50)

    def rotate(self, key, grid):
        if key == pygame.K_x:
            self.rotate_clockwise(grid)
        elif key == pygame.K_z:
            self.rotate_counter_clockwise(grid)

    def move(self, key, grid: Grid):
        position_change = 0
        illegal_move = False

        if key == pygame.K_LEFT:
            position_change = -1
            for pos in self.position:
                if (pos[1] == self.LEFT_BORDER or
                        grid.blocks[pos[0]][pos[1] + position_change].occupied):
                    illegal_move = True

        if key == pygame.K_RIGHT:
            position_change = 1
            for pos in self.position:
                if (pos[1] == self.RIGHT_BORDER or
                        grid.blocks[pos[0]][pos[1] + position_change].occupied):
                    illegal_move = True

        if not illegal_move:
            for i in range(len(self.position)):
                self.position[i][1] += position_change

    def rotate_clockwise(self, grid):
        pass

    def rotate_counter_clockwise(self, grid):
        pass

    def gravitate(self):
        for i in range(len(self.position)):
            self.position[i][0] += 1

    def rotated_piece_position(self, point: List[int], pivot_point: List[int],
                               rotation_matrix: Tuple[List[int], List[int]]) -> List[int]:
        relative_vector = self.get_relative_vector(point, pivot_point)
        transformed_vector = self.get_transformed_vector(rotation_matrix, relative_vector)
        return [pivot_point[0] + transformed_vector[0], pivot_point[1] + transformed_vector[1]]

    @staticmethod
    def get_transformed_vector(rotation_matrix: Tuple[List[int], List[int]],
                               relative_vector: Tuple[int, int]) -> Tuple[int, int]:
        transformed_x = rotation_matrix[0][0] * relative_vector[0] + rotation_matrix[0][1] * relative_vector[1]
        transformed_y = rotation_matrix[1][0] * relative_vector[0] + rotation_matrix[1][1] * relative_vector[1]
        return transformed_x, transformed_y

    @staticmethod
    def get_relative_vector(point, pivot_point) -> Tuple[int, int]:
        relative_x = point[0] - pivot_point[0]
        relative_y = point[1] - pivot_point[1]
        return relative_x, relative_y
