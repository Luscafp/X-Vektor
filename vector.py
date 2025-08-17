import pygame
import math

class Vector:
    def __init__(self, data):
        self.name = data.get('vetor', '') or data.get('name', '')
        self.modulo = data.get('modulo', 0)
        self.origem = data.get('origem', '')
        self.extremidade = data.get('extremidade', '')
        self.start_pos = data.get('correct_start', None)
        self.end_pos = data.get('correct_end', None)

    def draw(self, screen, board, color=(0, 0, 255), is_result=False):
        if self.start_pos and self.end_pos:
            start_x, start_y = board.get_pixel_pos(self.start_pos['col'], self.start_pos['row'])
            end_x, end_y = board.get_pixel_pos(self.end_pos['col'], self.end_pos['row'])
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)
            
            # Cabeça da seta adaptada à direção
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                ux = dx / length
                uy = dy / length
                arrow_length = 10
                arrow_width = 5
                p1 = (end_x - arrow_length * ux + arrow_width * uy, end_y - arrow_length * uy - arrow_width * ux)
                p2 = (end_x - arrow_length * ux - arrow_width * uy, end_y - arrow_length * uy + arrow_width * ux)
                pygame.draw.polygon(screen, color, [(end_x, end_y), p1, p2])