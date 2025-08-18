import pygame
import json
from board import Board
from vector import Vector

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
                if "Correto" in self.feedback:  # Se acertou na última tentativa
                    self.current_question_idx += 1
                    if self.current_question_idx >= len(self.questions):
                        self.feedback = "Jogo Concluído!"
                    self.reset_player_input()
                elif not self.player_start:
                    self.player_start = pos
                    self.feedback = ""  # Limpa feedback ao começar novo vetor
                elif not self.player_end:
                    self.player_end = pos
                    self.check_answer(q)

    def check_answer(self, q):
        correct = (self.player_start == q['correct_start'] and self.player_end == q['correct_end'])
        self.feedback = "Correto!" if correct else "Errado! Tente novamente."
        if correct:
            self.current_question_idx += 1
            if self.current_question_idx >= len(self.questions):
                self.feedback = "Jogo Concluído!"
        else:
            self.reset_player_input()

    def reset_player_input(self):
        self.player_start = None
        self.player_end = None

    def draw(self):
        self.board.draw(self.screen)
        q = self.get_current_question()

        # Exibir dados
        text = f"Nível {q['level']}"
        if q['level'] == 1:
            text += f" | Vetor: {q['vetor']} | Módulo: {q['modulo']} | Origem: {q['origem']} | Extremidade: {q['extremidade']}"
        else:
            text += f" | Operação: {q['operation']}"
            self.vectors = [Vector(v) for v in q['vetors']]
            for v in self.vectors:
                v.draw(self.screen, self.board, (255, 0, 0))  # Vetores iniciais em vermelho
        self.screen.blit(self.font.render(text, True, (0, 0, 0)), (10, self.board.offset_y + self.board.grid_height + 10))

        # Desenhar input do jogador
        if self.player_start and self.player_end:
            player_vector = Vector({'correct_start': self.player_start, 'correct_end': self.player_end})
            player_vector.draw(self.screen, self.board, color=(0, 0, 255))  # Vetor do jogador em azul

        if self.player_start:
            x, y = self.board.get_pixel_pos(self.player_start['col'], self.player_start['row'])
            pygame.draw.circle(self.screen, (0, 255, 0), (int(x), int(y)), 5)
        if self.player_end:
            x, y = self.board.get_pixel_pos(self.player_end['col'], self.player_end['row'])
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)

        # Feedback
        self.screen.blit(self.font.render(self.feedback, True, (0, 255, 0) if "Correto" in self.feedback else (255, 0, 0)), (10, self.board.offset_y + self.board.grid_height + 50))