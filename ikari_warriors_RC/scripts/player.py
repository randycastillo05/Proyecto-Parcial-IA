import pygame
import math
from scripts.utils.constants import *

class Player(pygame.sprite.Sprite):
    """Clase que representa al jugador"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Crear sprite temporal (un cuadrado verde por ahora)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.original_image = self.image.copy()
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición flotante para movimiento suave
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        
        # Atributos del jugador
        self.max_health = PLAYER_HEALTH
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.angle = 0  # Ángulo de rotación
        
        # Control de disparo
        self.shoot_cooldown = 0
        self.can_shoot = True
        self.shoot_request = False
        self.is_shooting = False
        
        # Power-ups activos
        self.speed_boost = 1.0
        self.damage_boost = 1.0
        self.fire_rate_boost = 1.0
        
        # Timers de power-ups
        self.speed_boost_timer = 0
        self.damage_boost_timer = 0
        self.fire_rate_boost_timer = 0
        
        # Efectos visuales
        self.flash_timer = 0
        self.flash_color = None
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Referencia al juego
        self.game = None
        
        # Estado del gamepad
        self.gamepad_shoot_held = False
        
    def handle_input(self, keys, mouse_pos, mouse_buttons, gamepad):
        """Maneja el input del jugador"""
        # Resetear velocidad
        self.velocity.x = 0
        self.velocity.y = 0
        
        # Input de gamepad si está disponible
        if gamepad:
            # Movimiento con stick izquierdo
            x_axis = gamepad.get_axis(0)  # Eje X del stick izquierdo
            y_axis = gamepad.get_axis(1)  # Eje Y del stick izquierdo
            
            # Aplicar zona muerta
            if abs(x_axis) > 0.1:
                self.velocity.x = x_axis * self.speed * self.speed_boost