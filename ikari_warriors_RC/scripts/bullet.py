import pygame
import math
from scripts.utils.constants import *

class Bullet(pygame.sprite.Sprite):
    """Clase para los proyectiles del juego"""
    
    def __init__(self, x, y, angle, damage=BULLET_DAMAGE, speed=BULLET_SPEED, owner=None):
        super().__init__()
        
        # Crear sprite
        self.image = pygame.Surface((6, 6))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición y movimiento
        self.pos = pygame.math.Vector2(x, y)
        self.angle = angle
        self.speed = speed
        
        # Calcular velocidad
        self.velocity = pygame.math.Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )
        
        # Propiedades
        self.damage = damage
        self.owner = owner  # Quien disparó (para evitar daño propio)
        self.lifetime = 3.0  # Segundos antes de desaparecer
        self.distance_traveled = 0
        self.max_distance = 800  # Distancia máxima
        
        # Trail effect
        self.trail_positions = []
        self.max_trail_length = 5
        
    def update(self, dt):
        """Actualiza la bala"""
        # Guardar posición anterior para el trail
        self.trail_positions.append(self.pos.copy())
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Mover
        movement = self.velocity * dt
        self.pos += movement
        self.rect.center = self.pos
        
        # Actualizar distancia recorrida
        self.distance_traveled += movement.length()
        
        # Actualizar lifetime
        self.lifetime -= dt
        
        # Verificar si debe desaparecer
        if (self.lifetime <= 0 or 
            self.distance_traveled >= self.max_distance or
            self.is_out_of_bounds()):
            self.kill()
    
    def is_out_of_bounds(self):
        """Verifica si la bala está fuera de la pantalla"""
        margin = 50
        return (self.pos.x < -margin or 
                self.pos.x > SCREEN_WIDTH + margin or
                self.pos.y < -margin or 
                self.pos.y > SCREEN_HEIGHT + margin)
    
    def draw_trail(self, screen):
        """Dibuja el trail de la bala"""
        if len(self.trail_positions) > 1:
            for i in range(1, len(self.trail_positions)):
                alpha = i / len(self.trail_positions)
                color = (255, 255, 0, int(alpha * 128))
                start_pos = self.trail_positions[i-1]
                end_pos = self.trail_positions[i]
                pygame.draw.line(screen, YELLOW, start_pos, end_pos, 2)


class Explosion(pygame.sprite.Sprite):
    """Efecto de explosión"""
    
    def __init__(self, x, y, radius=50, damage=50, duration=0.5):
        super().__init__()
        
        self.pos = pygame.math.Vector2(x, y)
        self.radius = radius
        self.max_radius = radius
        self.damage = damage
        self.duration = duration
        self.elapsed = 0
        self.has_damaged = False
        
        # Sprite temporal
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self, dt):
        """Actualiza la explosión"""
        self.elapsed += dt
        
        # Calcular progreso (0 a 1)
        progress = self.elapsed / self.duration
        
        if progress >= 1.0:
            self.kill()
            return
        
        # Expandir y desvanecer
        if progress < 0.3:
            # Fase de expansión
            self.radius = self.max_radius * (progress / 0.3)
        else:
            # Fase de desvanecimiento
            self.radius = self.max_radius
        
        # Actualizar visual
        self.update_visual(progress)
    
    def update_visual(self, progress):
        """Actualiza el efecto visual de la explosión"""
        self.image.fill((0, 0, 0, 0))  # Limpiar
        
        # Calcular alpha
        if progress < 0.3:
            alpha = 255
        else:
            alpha = int(255 * (1.0 - (progress - 0.3) / 0.7))
        
        # Dibujar círculos concéntricos
        colors = [(255, 255, 255), (255, 200, 0), (255, 100, 0)]
        
        for i, color in enumerate(colors):
            r = int(self.radius * (1.0 - i * 0.2))
            if r > 0:
                # Crear superficie temporal con alpha
                surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*color, alpha), (r, r), r)
                
                # Posicionar en el centro
                pos = (self.max_radius - r, self.max_radius - r)
                self.image.blit(surf, pos)
    
    def check_damage(self, target):
        """Verifica si el objetivo está en el radio de daño"""
        if self.has_damaged:
            return False
            
        distance = self.pos.distance_to(target.pos)
        
        if distance <= self.radius:
            # Calcular daño según distancia
            damage_factor = 1.0 - (distance / self.max_radius) * 0.5
            final_damage = int(self.damage * damage_factor)
            
            target.take_damage(final_damage)
            return True
            
        return False
    
    def draw_debug(self, screen):
        """Dibuja el radio de la explosión para debug"""
        pygame.draw.circle(screen, (255, 0, 0, 128), 
                          (int(self.pos.x), int(self.pos.y)), 
                          int(self.radius), 2)


class PowerUp(pygame.sprite.Sprite):
    """Power-ups que pueden dejar los enemigos"""
    
    def __init__(self, x, y, powerup_type="health"):
        super().__init__()
        
        self.powerup_type = powerup_type
        self.pos = pygame.math.Vector2(x, y)
        
        # Configurar según tipo
        if powerup_type == "health":
            self.color = GREEN
            self.value = 25
            self.size = 20
        elif powerup_type == "ammo":
            self.color = YELLOW
            self.value = 50
            self.size = 20
        elif powerup_type == "speed":
            self.color = BLUE
            self.value = 1.5  # Multiplicador
            self.duration = 5.0  # Segundos
            self.size = 20
        else:
            self.color = WHITE
            self.value = 0
            self.size = 20
        
        # Crear sprite
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Animación
        self.bob_offset = 0
        self.bob_speed = 2
        self.lifetime = 10.0  # Desaparece después de 10 segundos
        self.flash_timer = 0
        
    def update(self, dt):
        """Actualiza el power-up"""
        # Animación de flotación
        self.bob_offset += self.bob_speed * dt
        bob_y = math.sin(self.bob_offset) * 5
        
        self.rect.centery = self.pos.y + bob_y
        
        # Actualizar lifetime
        self.lifetime -= dt
        
        # Parpadear cuando queda poco tiempo
        if self.lifetime < 3.0:
            self.flash_timer += dt
            if self.flash_timer > 0.2:
                self.flash_timer = 0
                # Alternar visibilidad
                if self.image.get_alpha() == 255:
                    self.image.set_alpha(128)
                else:
                    self.image.set_alpha(255)
        
        # Eliminar si expira
        if self.lifetime <= 0:
            self.kill()
    
    def apply_to_player(self, player):
        """Aplica el efecto al jugador"""
        if self.powerup_type == "health":
            player.health = min(player.health + self.value, PLAYER_HEALTH)
            print(f"¡Vida +{self.value}!")
        elif self.powerup_type == "ammo":
            # TODO: Implementar munición
            print(f"¡Munición +{self.value}!")
        elif self.powerup_type == "speed":
            # TODO: Implementar buff de velocidad temporal
            print(f"¡Velocidad x{self.value} por {self.duration}s!")
        
        # Efecto de sonido
        # TODO: Reproducir sonido de power-up
        
        self.kill()


class BulletManager:
    """Gestiona todos los proyectiles del juego"""
    
    def __init__(self, bullet_group, explosion_group):
        self.bullets = bullet_group
        self.explosions = explosion_group
        self.bullet_pool