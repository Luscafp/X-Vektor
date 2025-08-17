import pygame

class Board:
    def __init__(self, width=800, height=600, cols=20, rows=15):
        self.width = width
        self.height = height
        self.cols = cols
        self.rows = rows
        self.cell_size = min(width // cols, height // rows)  # 40 para 800x600
        self.background = pygame.image.load('assets/background.png').convert()
        self.background = pygame.transform.scale(self.background, (width, height))  # Escala se necessário

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        
        # Desenhar linhas da grade
        for i in range(self.cols + 1):
            pygame.draw.line(screen, (0, 0, 0), (i * self.cell_size, 0), (i * self.cell_size, self.height))
        for j in range(self.rows + 1):
            pygame.draw.line(screen, (0, 0, 0), (0, j * self.cell_size), (self.width, j * self.cell_size))
        
        # Labels das colunas (topo, dentro da grade)
        font = pygame.font.SysFont(None, 24)
        for col in range(1, self.cols + 1):
            label = font.render(chr(64 + col), True, (0, 0, 0))
            screen.blit(label, ((col - 0.5) * self.cell_size - label.get_width() / 2, 10))
        
        # Labels das linhas (esquerda, ajustado para inversão)
        for row in range(1, self.rows + 1):
            label = font.render(str(row), True, (0, 0, 0))
            y = (self.rows - row + 0.5) * self.cell_size
            screen.blit(label, (10, y - label.get_height() / 2))
        
        # Dots vermelhos (topo)
        for col in range(1, self.cols + 1):
            pygame.draw.circle(screen, (255, 0, 0), ((col - 0.5) * self.cell_size, 5), 3)
        
        # Dots pretos (esquerda)
        for row in range(1, self.rows + 1):
            y = (self.rows - row + 0.5) * self.cell_size
            pygame.draw.circle(screen, (0, 0, 0), (5, y), 3)

    def get_grid_pos(self, mouse_x, mouse_y):
        col = mouse_x // self.cell_size + 1
        row = self.rows - (mouse_y // self.cell_size)
        if 1 <= col <= self.cols and 1 <= row <= self.rows:
            return {'row': row, 'col': col}
        return None

    def get_pixel_pos(self, col, row):
        x = (col - 0.5) * self.cell_size
        y = (self.rows - row + 0.5) * self.cell_size
        return (x, y)