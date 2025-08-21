import pygame
import os

class Board:
    def __init__(self, screen_width=1200, screen_height=800, cols=20, rows=15):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cols = cols
        self.rows = rows
        self.cell_size = 30  # Ajustado para caber com margens
        self.grid_width = self.cols * self.cell_size  # 600
        self.grid_height = self.rows * self.cell_size  # 450
        self.offset_x = (self.screen_width - self.grid_width) // 2  # ~100 para centralizar
        self.offset_y = 130  # Margem superior para logos/título

        self.background = None
        # Tenta carregar imagem de fundo; se não existir, usa cor sólida
        bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'background.png')
        if os.path.exists(bg_path):
            try:
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
            except Exception:
                self.background = None

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((245, 246, 252))

        # Desenhar linhas da grade com offsets
        for i in range(self.cols + 1):
            x = self.offset_x + i * self.cell_size
            pygame.draw.line(screen, (0, 0, 0), (x, self.offset_y), (x, self.offset_y + self.grid_height))
        for j in range(self.rows + 1):
            y = self.offset_y + j * self.cell_size
            pygame.draw.line(screen, (0, 0, 0), (self.offset_x, y), (self.offset_x + self.grid_width, y))

        # Labels das colunas (acima do grid, com distância)
        font = pygame.font.SysFont(None, 24)
        for col in range(1, self.cols + 1):
            label = font.render(chr(64 + col), True, (0, 0, 0))
            screen.blit(label, (self.offset_x + (col - 0.5) * self.cell_size - label.get_width() / 2, self.offset_y - 30))

        # Labels das linhas (à esquerda do grid, com distância, inversão)
        for row in range(1, self.rows + 1):
            label = font.render(str(row), True, (0, 0, 0))
            y = self.offset_y + (self.rows - row) * self.cell_size + self.cell_size / 2
            screen.blit(label, (self.offset_x - 40, y - label.get_height() / 2))  # Distância extra para visibilidade

        # Dots vermelhos (acima das letras)
        for col in range(1, self.cols + 1):
            pygame.draw.circle(screen, (255, 0, 0), (self.offset_x + (col - 0.5) * self.cell_size, self.offset_y - 10), 3)

        # Dots pretos (à esquerda dos números)
        for row in range(1, self.rows + 1):
            y = self.offset_y + (self.rows - row) * self.cell_size + self.cell_size / 2
            pygame.draw.circle(screen, (0, 0, 0), (self.offset_x - 20, y), 3)  # Distância para visibilidade

    def get_grid_pos(self, mouse_x, mouse_y):
        mouse_x -= self.offset_x
        mouse_y -= self.offset_y
        if mouse_x < 0 or mouse_x >= self.grid_width or mouse_y < 0 or mouse_y >= self.grid_height:
            return None
        col = mouse_x // self.cell_size + 1
        row = self.rows - (mouse_y // self.cell_size)
        if 1 <= col <= self.cols and 1 <= row <= self.rows:
            return {'row': row, 'col': col}
        return None

    def get_pixel_pos(self, col, row):
        x = self.offset_x + (col - 0.5) * self.cell_size
        y = self.offset_y + (self.rows - row) * self.cell_size + self.cell_size / 2
        return (x, y)
