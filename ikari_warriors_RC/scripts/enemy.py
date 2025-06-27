import pygame
import math
from scripts.utils.constants import *

class Enemy(pygame.sprite.Sprite):
    """Clase base para todos los enemigos"""
    
    def __init__(self, x, y, enemy_type=EnemyType.SOLDIER):
        super().__init__()
        
        # Sprite temporal (cuadrado rojo)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición y movimiento
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        
        # Atributos del enemigo
        self.enemy_type = enemy_type
        self.health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED
        self.sight_range = ENEMY_SIGHT_RANGE
        self.shoot_range = ENEMY_SHOOT_RANGE
        
        # Estado
        self.state = "patrol"  # patrol, chase, attack
        self.target = None
        self.path = []
        self.path_index = 0
        self.path_update_timer = 0
        self.path_update_cooldown = 0.5  # Actualizar path cada 0.5 segundos
        
        # Puntos de patrulla
        self.patrol_points = []
        self.current_patrol_index = 0
        self.setup_patrol_points()
        
        # Control de disparo
        self.shoot_cooldown = 0
        self.can_shoot = True
        
        # Referencias (se establecen desde Game)
        self.player = None
        self.pathfinder = None
        
    def setup_patrol_points(self):
        """Configura los puntos de patrulla del enemigo"""
        # Crear algunos puntos de patrulla alrededor de la posición inicial
        center_x, center_y = self.pos.x, self.pos.y
        offsets = [(100, 0), (0, 100), (-100, 0), (0, -100)]
        
        for dx, dy in offsets:
            patrol_x = center_x + dx
            patrol_y = center_y + dy
            # Mantener dentro de la pantalla
            patrol_x = max(50, min(SCREEN_WIDTH - 50, patrol_x))
            patrol_y = max(50, min(SCREEN_HEIGHT - 50, patrol_y))
            self.patrol_points.append((patrol_x, patrol_y))
    
    def update(self, dt):
        """Actualiza el estado del enemigo"""
        # Actualizar cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            self.can_shoot = False
        else:
            self.can_shoot = True
            
        self.path_update_timer += dt
        
        # Actualizar según el estado
        if self.state == "patrol":
            self.patrol_behavior(dt)
        elif self.state == "chase":
            self.chase_behavior(dt)
        elif self.state == "attack":
            self.attack_behavior(dt)
            
        # Detectar jugador
        if self.player:
            self.detect_player()
            
        # Mover enemigo
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        
    def detect_player(self):
        """Detecta si el jugador está en rango"""
        if not self.player:
            return
            
        distance = self.pos.distance_to(self.player.pos)
        
        # Si ve al jugador
        if distance <= self.sight_range:
            # TODO: Verificar línea de visión
            if self.state == "patrol":
                self.state = "chase"
                self.target = self.player
                print(f"Enemigo detectó al jugador!")
        else:
            # Perder al jugador si está muy lejos
            if self.state == "chase" and distance > self.sight_range * 1.5:
                self.state = "patrol"
                self.target = None
                self.path = []
                print(f"Enemigo perdió al jugador")
    
    def patrol_behavior(self, dt):
        """Comportamiento de patrulla"""
        if not self.patrol_points:
            return
            
        # Obtener punto de patrulla actual
        target_point = self.patrol_points[self.current_patrol_index]
        
        # Si necesitamos un nuevo path
        if not self.path or self.path_update_timer >= self.path_update_cooldown:
            if self.pathfinder:
                self.path = self.pathfinder.find_path(
                    (self.pos.x, self.pos.y),
                    target_point
                )
                self.path_index = 0
                self.path_update_timer = 0
        
        # Seguir el path
        if self.path:
            self.follow_path(dt)
            
            # Si llegamos al punto de patrulla
            if self.pos.distance_to(target_point) < 20:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
                self.path = []
    
    def chase_behavior(self, dt):
        """Comportamiento de persecución"""
        if not self.target:
            self.state = "patrol"
            return
            
        distance = self.pos.distance_to(self.target.pos)
        
        # Si está en rango de ataque
        if distance <= self.shoot_range:
            self.state = "attack"
            self.velocity = pygame.math.Vector2(0, 0)  # Detenerse para disparar
        else:
            # Actualizar path hacia el jugador
            if self.path_update_timer >= self.path_update_cooldown:
                if self.pathfinder:
                    self.path = self.pathfinder.find_path(
                        (self.pos.x, self.pos.y),
                        (self.target.pos.x, self.target.pos.y)
                    )
                    self.path_index = 0
                    self.path_update_timer = 0
            
            # Seguir el path
            if self.path:
                self.follow_path(dt)
    
    def attack_behavior(self, dt):
        """Comportamiento de ataque"""
        if not self.target:
            self.state = "patrol"
            return
            
        distance = self.pos.distance_to(self.target.pos)
        
        # Si el jugador se aleja, volver a perseguir
        if distance > self.shoot_range * 1.2:
            self.state = "chase"
        else:
            # Apuntar al jugador
            dx = self.target.pos.x - self.pos.x
            dy = self.target.pos.y - self.pos.y
            self.angle = math.atan2(dy, dx)
            
            # Disparar
            if self.can_shoot:
                self.shoot()
    
    def follow_path(self, dt):
        """Sigue el path calculado por A*"""
        if not self.path or self.path_index >= len(self.path):
            self.velocity = pygame.math.Vector2(0, 0)
            return
            
        # Obtener siguiente punto del path
        target_x = self.path[self.path_index][0] * TILE_SIZE + TILE_SIZE // 2
        target_y = self.path[self.path_index][1] * TILE_SIZE + TILE_SIZE // 2
        target_pos = pygame.math.Vector2(target_x, target_y)
        
        # Calcular dirección
        direction = target_pos - self.pos
        distance = direction.length()
        
        if distance < 10:  # Llegamos al punto
            self.path_index += 1
        else:
            # Mover hacia el punto
            if distance > 0:
                direction = direction.normalize()
                self.velocity = direction * self.speed
                self.angle = math.atan2(direction.y, direction.x)
    
    def shoot(self):
        """Dispara hacia el objetivo"""
        if self.can_shoot and self.target:
            # TODO: Crear bala
            print(f"Enemigo disparando!")
            self.shoot_cooldown = SHOOT_COOLDOWN * 1.5  # Enemigos disparan más lento
    
    def take_damage(self, damage):
        """Recibe daño"""
        self.health -= damage
        if self.health <= 0:
            self.kill()  # Eliminar del grupo de sprites
            print(f"Enemigo eliminado!")
            
    def draw_debug(self, screen):
        """Dibuja información de debug"""
        if self.state == "chase" and self.path:
            # Dibujar path
            if len(self.path) > 1:
                points = []
                for x, y in self.path:
                    world_x = x * TILE_SIZE + TILE_SIZE // 2
                    world_y = y * TILE_SIZE + TILE_SIZE // 2
                    points.append((world_x, world_y))
                    
                pygame.draw.lines(screen, YELLOW, False, points, 2)
        
        # Dibujar rango de visión
        pygame.draw.circle(screen, (255, 255, 0, 50), 
                          (int(self.pos.x), int(self.pos.y)), 
                          self.sight_range, 1)