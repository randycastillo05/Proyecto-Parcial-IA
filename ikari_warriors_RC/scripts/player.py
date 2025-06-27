import pygame
import math
from scripts.utils.constants import *

class Player(pygame.sprite.Sprite):
    """Clase que representa al jugador"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Crear sprite temporal (un cuadrado verde por ahora)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición flotante para movimiento suave
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        
        # Atributos del jugador
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.angle = 0  # Ángulo de rotación
        
        # Control de disparo
        self.shoot_cooldown = 0
        self.can_shoot = True
        
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
                self.velocity.x = x_axis * self.speed
            if abs(y_axis) > 0.1:
                self.velocity.y = y_axis * self.speed
                
            # Apuntado con stick derecho
            aim_x = gamepad.get_axis(3)  # Eje X del stick derecho
            aim_y = gamepad.get_axis(4)  # Eje Y del stick derecho
            
            if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
                self.angle = math.atan2(aim_y, aim_x)
                
            # Disparo con gatillo derecho
            if gamepad.get_axis(5) > 0.5:  # RT/R2
                self.shoot()
                
        else:
            # Movimiento con teclado
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.velocity.y = -self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.velocity.y = self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velocity.x = -self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velocity.x = self.speed
                
            # Normalizar velocidad diagonal
            if self.velocity.length() > 0:
                self.velocity = self.velocity.normalize() * self.speed
                
            # Apuntado con mouse
            dx = mouse_pos[0] - self.pos.x
            dy = mouse_pos[1] - self.pos.y
            self.angle = math.atan2(dy, dx)
            
            # Disparo con click izquierdo
            if mouse_buttons[0]:
                self.shoot()
    
    def update(self, dt):
        """Actualiza el estado del jugador"""
        # Actualizar cooldown de disparo
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            self.can_shoot = False
        else:
            self.can_shoot = True
            
        # Mover jugador
        self.pos += self.velocity * dt
        
        # Mantener dentro de la pantalla
        self.pos.x = max(PLAYER_SIZE//2, min(SCREEN_WIDTH - PLAYER_SIZE//2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE//2, min(SCREEN_HEIGHT - PLAYER_SIZE//2, self.pos.y))
        
        # Actualizar rect
        self.rect.center = self.pos
        
        # TODO: Rotar sprite según el ángulo
        
    def shoot(self):
        """Dispara un proyectil"""
        if self.can_shoot:
            # TODO: Crear bala
            print(f"¡Disparando! Ángulo: {math.degrees(self.angle):.1f}°")
            self.shoot_cooldown = SHOOT_COOLDOWN
            
    def take_damage(self, damage):
        """Recibe daño"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            # TODO: Manejar muerte del jugador