
import pygame
import json
import math
import os
from board import Board
from vector import Vector

class Game:
    STATE_MENU = 'menu'
    STATE_PLAYING = 'playing'
    STATE_FINISHED = 'finished'

    def __init__(self, screen):
        self.screen = screen
        self.board = Board(1200, 800, 20, 15)
        self.font = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_big = pygame.font.SysFont(None, 48)

        self.state = Game.STATE_MENU
        self.difficulty = None
        self.questions = []
        self.current_index = 0
        self.player_start = None
        self.player_end = None
        self.feedback = ''
        self.awaiting_next = False
        self.solved = set()
        self.toast = None

        # Sons
        self.sound_correct = self.load_sound('assets/correct.wav')
        self.sound_wrong = self.load_sound('assets/wrong.wav')

        # Logos
        self.logo_uema = self.load_logo('assets/logo_uema.png')
        self.logo_xvector = self.load_logo('assets/logo_xvector.png')
        self.logo_uemanet = self.load_logo('assets/logo_uemanet.png')

        self.menu_buttons = {
            'facil': pygame.Rect(0, 0, 260, 60),
            'dificil': pygame.Rect(0, 0, 260, 60),
        }
        self.next_button = pygame.Rect(0, 0, 180, 48)
        self.clear_button = pygame.Rect(0, 0, 160, 40)
        self.menu_button = pygame.Rect(0, 0, 160, 40)

    def load_sound(self, path):
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                return None
        return None

    def load_logo(self, path):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                h = 70
                scale = h / img.get_height()
                w = int(img.get_width() * scale)
                return pygame.transform.smoothscale(img, (w, h))
            except Exception:
                return None
        return None

    def load_questions_file(self, path):
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('questions', [])

    def start_game(self, difficulty):
        self.difficulty = difficulty
        if difficulty == 'facil':
            self.questions = self.load_questions_file('questions.json')
        else:
            self.questions = self.load_questions_file('questions_hard.json')
        self.current_index = 0
        self.player_start = None
        self.player_end = None
        self.feedback = ''
        self.awaiting_next = False
        self.solved.clear()
        self.state = Game.STATE_PLAYING if self.questions else Game.STATE_MENU
        if not self.questions:
            self.toast = ('Questões difíceis ainda não disponíveis.', pygame.time.get_ticks() + 2000)

    def update(self, event):
        if self.toast and pygame.time.get_ticks() > self.toast[1]:
            self.toast = None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = Game.STATE_MENU
            return
        if self.state == Game.STATE_MENU:
            self.update_menu(event)
        elif self.state in (Game.STATE_PLAYING, Game.STATE_FINISHED):
            self.update_play(event)

    def update_menu(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        mx, my = event.pos
        sw, sh = self.screen.get_size()
        spacing = 20
        total_h = 2 * 60 + spacing
        start_y = sh // 2 - total_h // 2
        for name, rect in self.menu_buttons.items():
            rect.centerx = sw // 2
            rect.y = start_y if name == 'facil' else start_y + 60 + spacing
        if self.menu_buttons['facil'].collidepoint(mx, my):
            self.start_game('facil')
        elif self.menu_buttons['dificil'].collidepoint(mx, my):
            self.start_game('dificil')

    def update_play(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.awaiting_next:
                    self.go_next()
                elif self.state == Game.STATE_FINISHED:
                    self.state = Game.STATE_MENU
                return
            if event.key == pygame.K_r:
                self.reset_player_input()
                self.feedback = ''
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            self.position_action_buttons()
            if self.state == Game.STATE_FINISHED:
                if self.menu_button.collidepoint(mx, my):
                    self.state = Game.STATE_MENU
                return
            if self.awaiting_next and self.next_button.collidepoint(mx, my):
                self.go_next()
                return
            if self.clear_button.collidepoint(mx, my):
                self.reset_player_input()
                self.feedback = ''
                return
            if self.awaiting_next:
                return
            pos = self.board.get_grid_pos(mx, my)
            if pos:
                if not self.player_start:
                    self.player_start = pos
                    self.feedback = ''
                elif not self.player_end:
                    self.player_end = pos
                    self.check_answer(self.questions[self.current_index])
                else:
                    self.reset_player_input()
                    self.player_start = pos
                    self.feedback = ''

    def position_action_buttons(self):
        sw, sh = self.screen.get_size()
        base_y = self.board.offset_y + self.board.grid_height + 90
        self.clear_button.size = (160, 40)
        self.clear_button.center = (sw//2 - 120, base_y)
        self.menu_button.size = (160, 40)
        self.menu_button.center = (sw//2 + 120, base_y)
        self.next_button.size = (180, 48)
        self.next_button.center = (sw//2, base_y + 55)

    def go_next(self):
        self.awaiting_next = False
        self.feedback = ''
        self.reset_player_input()
        self.current_index += 1
        self.solved.clear()
        if self.current_index >= len(self.questions):
            self.state = Game.STATE_FINISHED

    def check_answer(self, q):
        correct = (self.player_start == q['correct_start'] and self.player_end == q['correct_end'])
        if correct:
            self.feedback = 'Correto!'
            if self.sound_correct: self.sound_correct.play()
            self.solved.add(self.current_index)
            self.awaiting_next = True
        else:
            self.feedback = 'Errado! Tente novamente.'
            if self.sound_wrong: self.sound_wrong.play()

    def reset_player_input(self):
        self.player_start = None
        self.player_end = None

    def draw(self):
        if self.state == Game.STATE_MENU:
            self.draw_menu()
            return
        self.board.draw(self.screen)
        if self.state != Game.STATE_FINISHED:
            self.draw_question_and_vectors()
            self.draw_feedback_and_controls()
            self.draw_progress_bar()
        else:
            self.draw_finished()
        self.draw_logos()
        if self.toast:
            self.draw_toast(self.toast[0])

    def draw_menu(self):
        if self.board.background:
            self.screen.blit(self.board.background, (0, 0))
        else:
            self.screen.fill((20, 22, 30))
        sw, sh = self.screen.get_size()
        # title = self.font_big.render('X-Vector', True, (255, 255, 255))
        subtitle = self.font.render('Escolha a dificuldade', True, (255, 0, 0))
        # self.screen.blit(title, title.get_rect(center=(sw//2, sh//2 - 140)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(sw//2, sh//2 - 90)))
        spacing = 20
        total_h = 2 * 60 + spacing
        start_y = sh // 2 - total_h // 2
        for name, rect in self.menu_buttons.items():
            rect.width = 260
            rect.height = 60
            rect.centerx = sw // 2
            rect.y = start_y if name == 'facil' else start_y + 60 + spacing
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            color = (60, 130, 246) if hovered else (40, 110, 226)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            label = self.font.render('Questões Fáceis' if name == 'facil' else 'Questões Difíceis', True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=rect.center))
        tip = self.font_small.render('Dica: ESC volta ao menu.', True, (200, 200, 200))
        self.screen.blit(tip, tip.get_rect(center=(sw//2, sh - 40)))
        self.draw_logos()
        if self.toast:
            self.draw_toast(self.toast[0])

    def draw_question_and_vectors(self):
        q = self.questions[self.current_index]
        sw = self.screen.get_width()
        for i in sorted(self.solved):
            if 0 <= i < len(self.questions):
                Vector(self.questions[i]).draw(self.screen, self.board, (0, 180, 0))
        question_text = f"Vetor: {q.get('vetor', '')} | Módulo: {q.get('modulo', '')} | Origem: {q.get('origem', '')} | Extremidade: {q.get('extremidade', '')}"
        question_surface = self.font.render(f"Q{self.current_index + 1}/{len(self.questions)} | {question_text}", True, (0, 0, 0))
        question_rect = question_surface.get_rect(center=(sw//2, self.board.offset_y + self.board.grid_height + 30))
        self.screen.blit(question_surface, question_rect)
        if self.player_start and self.player_end:
            player_vector = Vector({'correct_start': self.player_start, 'correct_end': self.player_end})
            player_vector.draw(self.screen, self.board, color=(0, 0, 255))
        if self.player_start:
            x, y = self.board.get_pixel_pos(self.player_start['col'], self.player_start['row'])
            pygame.draw.circle(self.screen, (0, 255, 0), (int(x), int(y)), 5)
        if self.player_end:
            x, y = self.board.get_pixel_pos(self.player_end['col'], self.player_end['row'])
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)

    def draw_feedback_and_controls(self):
        sw = self.screen.get_width()
        if self.feedback:
            size_factor = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
            feedback_font = pygame.font.SysFont(None, int(32 * size_factor))
            color = (0, 200, 0) if 'Correto' in self.feedback else (220, 0, 0)
            feedback_surface = feedback_font.render(self.feedback, True, color)
            feedback_rect = feedback_surface.get_rect(center=(sw//2, self.board.offset_y + self.board.grid_height + 70))
            self.screen.blit(feedback_surface, feedback_rect)
        self.position_action_buttons()
        self.draw_button(self.clear_button, 'Limpar (R)')
        self.draw_button(self.menu_button, 'Menu (Esc)')
        if self.awaiting_next:
            self.draw_button(self.next_button, 'Próxima (Enter/Espaço)')

    def draw_progress_bar(self):
        sw = self.screen.get_width()
        total = len(self.questions)
        if total <= 0: return
        done = len(self.solved)
        width = 400
        height = 10
        x = sw//2 - width//2
        y = self.board.offset_y - 50
        pygame.draw.rect(self.screen, (200, 200, 200), pygame.Rect(x, y, width, height), border_radius=6)
        if done > 0:
            filled = int(width * done / total)
            pygame.draw.rect(self.screen, (60, 130, 246), pygame.Rect(x, y, filled, height), border_radius=6)
        label = self.font_small.render(f"Progresso: {done}/{total}", True, (50, 50, 50))
        self.screen.blit(label, (x + width + 12, y - 6))

    def draw_finished(self):
        sw, sh = self.screen.get_size()
        msg = self.font_big.render('Parabéns! Você concluiu todas as questões.', True, (0, 120, 0))
        self.screen.blit(msg, msg.get_rect(center=(sw//2, self.board.offset_y + self.board.grid_height//2)))
        self.position_action_buttons()
        self.draw_button(self.menu_button, 'Voltar ao Menu (Esc)')

    def draw_button(self, rect, text):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = (60, 130, 246) if hovered else (40, 110, 226)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_logos(self):
        sw = self.screen.get_width()
        if self.logo_uema:
            self.screen.blit(self.logo_uema, (20, 20))
        if self.logo_xvector:
            rect = self.logo_xvector.get_rect(midtop=(sw//2, 20))
            self.screen.blit(self.logo_xvector, rect)
        if self.logo_uemanet:
            rect = self.logo_uemanet.get_rect(topright=(sw-20, 20))
            self.screen.blit(self.logo_uemanet, rect)

    def draw_toast(self, text):
        sw, sh = self.screen.get_size()
        pad = 12
        surf = self.font_small.render(text, True, (255, 255, 255))
        rect = surf.get_rect()
        rect.center = (sw//2, sh - 80)
        bg = pygame.Rect(rect.x - pad, rect.y - pad, rect.width + 2*pad, rect.height + 2*pad)
        pygame.draw.rect(self.screen, (0, 0, 0), bg, border_radius=8)
        self.screen.blit(surf, rect)