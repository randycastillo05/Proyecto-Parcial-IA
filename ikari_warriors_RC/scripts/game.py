import pygame
from scripts.player import Player
from scripts.utils.constants import *
from scripts.utils.resources import ResourceManager

class Game:
    """Clase principal que maneja el estado del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.PLAYING  # Por ahora empezamos directo
        self.resource_manager = ResourceManager()
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        
        # Crear jugador
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Inicializar gamepad si está disponible
        self.init_gamepad()
        
    def init_gamepad(self):
        """Inicializa el gamepad si está conectado"""
        pygame.joystick.init()
        self.gamepad = None
        
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad detectado: {self.gamepad.get_name()}")
        else:
            print("No se detectó gamepad. Usando teclado y mouse.")
    
    def update(self, dt, events):
        """Actualiza la lógica del juego"""
        if self.state == GameState.PLAYING:
            # Obtener input
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            
            # Actualizar jugador con input
            self.player.handle_input(keys, mouse_pos, mouse_buttons, self.gamepad)
            
            # Actualizar todos los sprites
            self.all_sprites.update(dt)
            
            # Verificar colisiones
            self.check_collisions()
            
        elif self.state == GameState.MENU:
            # TODO: Implementar lógica del menú
            pass
            
    def check_collisions(self):
        """Verifica colisiones entre entidades"""
        # TODO: Implementar colisiones
        pass
    
    def draw(self):
        """Dibuja todo en pantalla"""
        # Limpiar pantalla
        self.screen.fill(DARK_GREEN)
        
        if self.state == GameState.PLAYING:
            # Dibujar sprites
            self.all_sprites.draw(self.screen)
            
            # Dibujar UI
            self.draw_ui()
            
        elif self.state == GameState.MENU:
            # TODO: Dibujar menú
            pass
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Dibujar barra de vida
        health_width = int((self.player.health / PLAYER_HEALTH) * 200)
        health_rect = pygame.Rect(10, 10, health_width, 20)
        border_rect = pygame.Rect(10, 10, 200, 20)
        
        pygame.draw.rect(self.screen, RED, health_rect)
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)
        
        # TODO: Agregar más elementos de UI (munición, score, etc.)