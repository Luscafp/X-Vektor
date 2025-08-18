import pygame
import json
from board import Board
from vector import Vector
import math

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board(1200, 800, 20, 15)  # Ajustado para nova resolução
        self.font = pygame.font.SysFont(None, 32)
        self.questions = self.load_questions()
        self.current_level = 1
        self.current_question_idx = 0
        self.player_start = None
        self.player_end = None
        self.feedback = ""
        self.vectors = []  # Para Nível 2

    def load_questions(self):
        with open('questions.json', 'r') as f:
            return json.load(f)['questions']

    def get_current_question(self):
        return self.questions[self.current_question_idx]

    def update(self, event):
        q = self.get_current_question()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = self.board.get_grid_pos(*event.pos[:2])
            if pos:
                if "Correto" in self.feedback and self.player_start and self.player_end:
                    # Só avança se já tiver um vetor completo e feedback de correto
                    if self.current_level < 2 or self.current_question_idx < len(self.questions) - 1:
                        self.reset_player_input()
                    else:
                        self.feedback = "Jogo Concluído!"
                elif not self.player_start:
                    self.player_start = pos
                    self.feedback = ""
                elif not self.player_end:
                    self.player_end = pos
                    self.check_answer(q)
                else:
                    # Se já tem ambos pontos, permite reiniciar com novo clique
                    self.reset_player_input()
                    self.player_start = pos
                    self.feedback = ""

    def check_answer(self, q):
        correct = (self.player_start == q['correct_start'] and self.player_end == q['correct_end'])
        self.feedback = "Correto!" if correct else "Errado! Tente novamente."
        
        if correct:
            # Verifica se ainda há questões no nível atual
            next_idx = self.current_question_idx + 1
            if next_idx < len(self.questions) and self.questions[next_idx]['level'] == self.current_level:
                self.current_question_idx = next_idx
            else:
                # Avança para o próximo nível ou finaliza
                self.current_level += 1
                if self.current_level > 2:  # Assumindo que temos apenas 2 níveis
                    self.feedback = "Jogo Concluído!"

    def reset_player_input(self):
        self.player_start = None
        self.player_end = None

    def draw(self):
        self.board.draw(self.screen)
        q = self.get_current_question()

        # Centralizar textos
        screen_width = self.screen.get_width()
        
        # Texto da operação (centralizado abaixo do grid)
        if q['level'] == 1:
            question_text = f"Vetor: {q['vetor']} | Módulo: {q['modulo']} | Origem: {q['origem']} | Extremidade: {q['extremidade']}"
        else:
            question_text = f"Operação: {q['operation']}"
            self.vectors = [Vector(v) for v in q['vetors']]
            for v in self.vectors:
                v.draw(self.screen, self.board, (255, 0, 0))
        
        # Renderizar texto da questão
        question_surface = self.font.render(f"Nível {q['level']} | {question_text}", True, (0, 0, 0))
        question_rect = question_surface.get_rect(center=(screen_width//2, self.board.offset_y + self.board.grid_height + 30))
        self.screen.blit(question_surface, question_rect)

        # Desenhar input do jogador
        if self.player_start and self.player_end:
            player_vector = Vector({'correct_start': self.player_start, 'correct_end': self.player_end})
            player_vector.draw(self.screen, self.board, color=(0, 0, 255))

        # Desenhar pontos de início e fim
        if self.player_start:
            x, y = self.board.get_pixel_pos(self.player_start['col'], self.player_start['row'])
            pygame.draw.circle(self.screen, (0, 255, 0), (int(x), int(y)), 5)
        if self.player_end:
            x, y = self.board.get_pixel_pos(self.player_end['col'], self.player_end['row'])
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)

            # Desenhar todos os vetores corretos do nível atual
        for i in range(self.current_question_idx):
            if self.questions[i]['level'] == self.current_level:
                correct_vec = Vector(self.questions[i])
                correct_vec.draw(self.screen, self.board, (0, 255, 0))  # Verde para vetores corretos
        
        # Feedback com animação
        if self.feedback:
            # Criar efeito de pulso (tamanho oscilante)
            size_factor = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
            feedback_font = pygame.font.SysFont(None, int(32 * size_factor))
            color = (0, 255, 0) if "Correto" in self.feedback else (255, 0, 0)
            feedback_surface = feedback_font.render(self.feedback, True, color)
            feedback_rect = feedback_surface.get_rect(center=(screen_width//2, self.board.offset_y + self.board.grid_height + 80))
            self.screen.blit(feedback_surface, feedback_rect)