"Ikari Warriors RC"

import pygame
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.game import Game
from scripts.menu import Menu
from scripts.utils.constants import *

class IkariWarriorsGame:
    """Clase principal que maneja el flujo del juego"""
    
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.running = True
        self.current_state = GameState.MENU
        
        # Crear estados
        self.menu = Menu(self.screen)
        self.game = None
        
        # Delta time
        self.dt = 0
        
        # Música de fondo
        self.init_music()
        
    def init_music(self):
        """Inicializa la música del juego"""
        # TODO: Cargar música real
        # pygame.mixer.music.load("assets/music/menu_theme.mp3")
        # pygame.mixer.music.set_volume(0.5)
        # pygame.mixer.music.play(-1)  # Loop infinito
        pass
    
    def new_game(self):
        """Inicia un nuevo juego"""
        self.game = Game(self.screen)
        self.current_state = GameState.PLAYING
        
        # TODO: Cambiar música
        # pygame.mixer.music.load("assets/music/game_theme.mp3")
        # pygame.mixer.music.play(-1)
    
    def handle_events(self):
        """Maneja los eventos globales"""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return []
            
            # Eventos específicos del estado actual
            if self.current_state == GameState.MENU:
                action = self.menu.handle_event(event)
                if action == "start":
                    self.new_game()
                elif action == "quit":
                    self.running = False
                    return []
                    
            elif self.current_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.current_state = GameState.PAUSED
                        
            elif self.current_state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.current_state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        self.current_state = GameState.MENU
                        self.game = None
                        
            elif self.current_state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.new_game()
                    elif event.key == pygame.K_m:
                        self.current_state = GameState.MENU
                        self.game = None
        
        return events
    
    def update(self):
        """Actualiza la lógica del juego"""
        # Obtener eventos
        events = self.handle_events()
        
        # Actualizar según el estado
        if self.current_state == GameState.MENU:
            self.menu.update(self.dt)
            
        elif self.current_state == GameState.PLAYING:
            if self.game:
                self.game.update(self.dt, events)
                
                # Verificar cambio de estado
                if self.game.state == GameState.GAME_OVER:
                    self.current_state = GameState.GAME_OVER
                    
        elif self.current_state == GameState.PAUSED:
            # No actualizar nada cuando está pausado
            pass
    
    def draw(self):
        """Dibuja en pantalla"""
        # Limpiar pantalla
        self.screen.fill(BLACK)
        
        # Dibujar según el estado
        if self.current_state == GameState.MENU:
            self.menu.draw()
            
        elif self.current_state == GameState.PLAYING:
            if self.game:
                self.game.draw()
                
        elif self.current_state == GameState.PAUSED:
            if self.game:
                self.game.draw()
            self.draw_pause_overlay()
            
        elif self.current_state == GameState.GAME_OVER:
            if self.game:
                self.game.draw()
                
        # Actualizar pantalla
        pygame.display.flip()
    
    def draw_pause_overlay(self):
        """Dibuja la pantalla de pausa"""
        # Oscurecer pantalla
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        pause_text = font.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = small_font.render("ESC - Continuar", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(resume_text, resume_rect)
        
        quit_text = small_font.render("Q - Volver al menú", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(quit_text, quit_rect)
    
    def run(self):
        """Bucle principal del juego"""
        print("=== IKARI WARRIORS CLONE ===")
        print("Iniciando juego...")
        
        while self.running:
            # Calcular delta time
            self.dt = self.clock.tick(FPS) / 1000.0  # Convertir a segundos
            
            # Actualizar
            self.update()
            
            # Dibujar
            self.draw()
            
            # Mostrar FPS en el título
            fps = self.clock.get_fps()
            pygame.display.set_caption(f"{TITLE} - FPS: {fps:.0f}")
        
        # Cerrar
        pygame.quit()
        sys.exit()
        print("Juego cerrado.")

def main():
    """Punto de entrada del programa"""
    game = IkariWarriorsGame()
    game.run()

if __name__ == "__main__":
    main()

