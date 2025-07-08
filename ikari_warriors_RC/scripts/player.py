"""
Randy Castillo
Módulo del Jugador
Contiene la clase Player que representa al jugador
"""

import pygame
import math
import os

# Constantes
PLAYER_SPEED = 5
PLAYER_SIZE = 32
SHOOT_COOLDOWN = 10

# Colores
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

def load_sprite(path, size=None, color_fallback=None):
    """Intenta cargar un sprite, si no existe usa un color"""
    if os.path.exists(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            return image
        except:
            pass
    
    # Fallback: crear superficie con color
    if size:
        surface = pygame.Surface(size)
        surface.fill(color_fallback or WHITE)
        return surface
    return None

class Bullet(pygame.sprite.Sprite):
    """Clase para las balas"""
    def __init__(self, x, y, direction):
        super().__init__()
        
        # Intentar cargar sprite de bala
        self.image = load_sprite("assets/images/bullet.png", (8, 16), WHITE)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10
        self.direction = direction
        
        # Rotar la bala según la dirección
        angle = math.atan2(-direction[1], direction[0]) * 180 / math.pi - 90
        self.image = pygame.transform.rotate(self.image, angle)
        
    def update(self):
        """Actualiza la posición de la bala"""
        # Mover según dirección
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # Eliminar si sale de pantalla
        if (self.rect.bottom < 0 or self.rect.top > 600 or 
            self.rect.right < 0 or self.rect.left > 800):
            self.kill()

class Player(pygame.sprite.Sprite):
    """Clase del jugador"""
    def __init__(self, x, y):
        super().__init__()
        
        # Cargar sprites del jugador
        self.sprites = {
            'up': load_sprite("assets/images/player_up.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN),
            'down': load_sprite("assets/images/player_down.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN),
            'left': load_sprite("assets/images/player_left.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN),
            'right': load_sprite("assets/images/player_right.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN)
        }
        
        # Si no hay sprites direccionales, intentar cargar uno general
        if not os.path.exists("assets/images/player_up.png"):
            default_sprite = load_sprite("assets/images/player.png", (PLAYER_SIZE, PLAYER_SIZE), GREEN)
            self.sprites = {
                'up': default_sprite,
                'down': default_sprite,
                'left': default_sprite,
                'right': default_sprite
            }
        
        # Sprite inicial
        self.image = self.sprites['up']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Atributos
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.facing_direction = (0, -1)  # Mirando hacia arriba por defecto
        self.current_sprite = 'up'
        
    def move(self, dx, dy, walls):
        """Mueve al jugador"""
        if dx != 0 or dy != 0:
            # Normalizar el vector de movimiento
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
                
                # Actualizar dirección de mirada y sprite
                self.facing_direction = (dx, dy)
                
                # Cambiar sprite según dirección
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self.current_sprite = 'right'
                    else:
                        self.current_sprite = 'left'
                else:
                    if dy > 0:
                        self.current_sprite = 'down'
                    else:
                        self.current_sprite = 'up'
                
                self.image = self.sprites[self.current_sprite]
            
            # Intentar mover en X
            old_x = self.rect.x
            self.rect.x += dx * self.speed
            
            # Verificar colisiones con paredes
            if pygame.sprite.spritecollide(self, walls, False):
                self.rect.x = old_x
            
            # Mantener dentro de pantalla
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > 800:
                self.rect.right = 800
                
            # Intentar mover en Y
            old_y = self.rect.y
            self.rect.y += dy * self.speed
            
            # Verificar colisiones con paredes
            if pygame.sprite.spritecollide(self, walls, False):
                self.rect.y = old_y
                
            # Mantener dentro de pantalla
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > 600:
                self.rect.bottom = 600
    
    def shoot(self):
        """Dispara una bala"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            
            # Crear bala
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.facing_direction)
            
            # Sonido de disparo
            try:
                sound = pygame.mixer.Sound("assets/sounds/fw_01.0gg")
                sound.set_volume(0.3)
                sound.play()
            except:
                pass
                
            return bullet
        return None
    
    def update(self):
        """Actualiza el estado del jugador"""
        # Reducir cooldown de disparo
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1