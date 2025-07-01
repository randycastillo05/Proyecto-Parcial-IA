import pygame
import math
import time
from scripts.utils.constants import *
from scripts.ai.behavior_tree import BehaviorTree
from scripts.ai.enemy_behaviors import EnemyBehaviorFactory

class Enemy(pygame.sprite.Sprite):
    """Clase base para todos los enemigos con árbol de comportamiento"""
    
    def __init__(self, x, y, enemy_type=EnemyType.SOLDIER):
        super().__init__()
        
        # Configuración según tipo de enemigo
        self.enemy_type = enemy_type
        self.setup_enemy_stats()
        
        # Sprite temporal (color según tipo)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.original_image = self.image.copy()
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición y movimiento
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        
        # Sistema de vida
        self.health = self.max_health
        
        # Path y navegación
        self.path = []
        self.path_index = 0
        self.path_update_timer = 0
        self.path_update_cooldown = 0.5
        
        # Puntos de patrulla
        self.patrol_points = []
        self.current_patrol_index = 0
        self.setup_patrol_points()
        
        # Control de disparo
        self.shoot_cooldown = 0
        self.can_shoot = True
        self.last_shot_time = 0
        
        # Buffs (del oficial)
        self.speed_buff = 1.0
        self.accuracy_buff = 1.0
        self.damage_buff = 1.0
        
        # Efectos visuales
        self.flash_color = None
        self.flash_timer = 0
        
        # Referencias (se establecen desde Game)
        self.player = None
        self.pathfinder = None
        self.game = None
        
        # Crear árbol de comportamiento
        self.behavior_tree = EnemyBehaviorFactory.create_behavior_tree(enemy_type)
        
        # Última posición conocida del jugador
        self.last_known_player_pos = None
        
        # Para debug
        self.current_behavior = "idle"
        
    def setup_enemy_stats(self):
        """Configura las estadísticas según el tipo de enemigo"""
        if self.enemy_type == EnemyType.SOLDIER:
            self.max_health = 50
            self.speed = 100
            self.sight_range = 200
            self.shoot_range = 150
            self.shoot_rate = 0.5  # Disparos por segundo
            self.accuracy = 0.7
            self.color = RED
            
        elif self.enemy_type == EnemyType.ELITE:
            self.max_health = 75
            self.speed = 120
            self.sight_range = 250
            self.shoot_range = 180
            self.shoot_rate = 0.8
            self.accuracy = 0.85
            self.color = (139, 0, 0)  # Rojo oscuro
            
        elif self.enemy_type == EnemyType.SNIPER:
            self.max_health = 40
            self.speed = 80
            self.sight_range = 400
            self.shoot_range = 350
            self.shoot_rate = 0.3
            self.accuracy = 0.95
            self.color = (128, 0, 128)  # Púrpura
            
        elif self.enemy_type == EnemyType.KAMIKAZE:
            self.max_health = 30
            self.speed = 180
            self.sight_range = 150
            self.shoot_range = 0  # No dispara
            self.shoot_rate = 0
            self.accuracy = 0
            self.color = (255, 165, 0)  # Naranja
            
        elif self.enemy_type == EnemyType.OFFICER:
            self.max_health = 100
            self.speed = 90
            self.sight_range = 200
            self.shoot_range = 120
            self.shoot_rate = 0.4
            self.accuracy = 0.6
            self.color = (0, 100, 0)  # Verde oscuro
    
    def setup_patrol_points(self):
        """Configura los puntos de patrulla del enemigo"""
        center_x, center_y = self.pos.x, self.pos.y
        
        # Diferentes patrones según el tipo
        if self.enemy_type == EnemyType.SNIPER:
            # Francotiradores buscan esquinas
            self.patrol_points = [
                (100, 100),
                (SCREEN_WIDTH - 100, 100),
                (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
                (100, SCREEN_HEIGHT - 100)
            ]
        elif self.enemy_type == EnemyType.KAMIKAZE:
            # Kamikazes patrullan agresivamente
            offsets = [(150, 0), (0, 150), (-150, 0), (0, -150)]
        else:
            # Patrulla normal
            offsets = [(100, 0), (0, 100), (-100, 0), (0, -100)]
        
        if self.enemy_type != EnemyType.SNIPER:
            for dx, dy in offsets:
                patrol_x = center_x + dx
                patrol_y = center_y + dy
                patrol_x = max(50, min(SCREEN_WIDTH - 50, patrol_x))
                patrol_y = max(50, min(SCREEN_HEIGHT - 50, patrol_y))
                self.patrol_points.append((patrol_x, patrol_y))
    
    def update(self, dt):
        """Actualiza el estado del enemigo usando el árbol de comportamiento"""
        # Actualizar timers
        self.path_update_timer += dt
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            self.can_shoot = False
        else:
            self.can_shoot = True
            
        # Actualizar efectos visuales
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_color = None
                self.image.fill(self.color)
        
        # Preparar blackboard para el árbol
        blackboard_data = {
            "enemy": self,
            "player": self.player,
            "pathfinder": self.pathfinder,
            "game": self.game,
            "grid": self.pathfinder.grid if self.pathfinder else None,
            "dt": dt,
            "current_time": time.time(),
            "all_enemies": self.game.enemies if self.game else []
        }
        
        # Guardar última posición conocida del jugador si es visible
        if self.player and self.can_see_player():
            self.last_known_player_pos = (self.player.pos.x, self.player.pos.y)
            blackboard_data["last_player_position"] = self.last_known_player_pos
        elif self.last_known_player_pos:
            blackboard_data["last_player_position"] = self.last_known_player_pos
        
        # Ejecutar árbol de comportamiento
        self.behavior_tree.tick(blackboard_data)
        
        # Procesar solicitudes del árbol
        self.process_tree_requests(blackboard_data)
        
        # Aplicar buffs al movimiento
        actual_speed = self.speed * self.speed_buff
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * actual_speed
        
        # Mover enemigo
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        
        # Mantener dentro de la pantalla
        self.pos.x = max(PLAYER_SIZE//2, min(SCREEN_WIDTH - PLAYER_SIZE//2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE//2, min(SCREEN_HEIGHT - PLAYER_SIZE//2, self.pos.y))
        
        # Actualizar sprite según ángulo
        self.update_sprite()
    
    def can_see_player(self):
        """Verifica si puede ver al jugador"""
        if not self.player:
            return False
            
        distance = self.pos.distance_to(self.player.pos)
        
        if distance <= self.sight_range:
            # TODO: Verificar línea de visión con raycasting
            return True
            
        return False
    
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
        if self.can_shoot and self.player:
            # Aplicar buff de precisión
            actual_accuracy = min(1.0, self.accuracy * self.accuracy_buff)
            
            # TODO: Crear bala con precisión
            if self.game:
                # Calcular dispersión según precisión
                import random
                spread = (1.0 - actual_accuracy) * 0.5
                angle_offset = random.uniform(-spread, spread)
                
                final_angle = self.angle + angle_offset
                
                # Solicitar creación de bala
                self.behavior_tree.blackboard["bullet_request"] = {
                    "position": self.pos.copy(),
                    "angle": final_angle,
                    "damage": BULLET_DAMAGE * self.damage_buff,
                    "owner": self
                }
            
            self.shoot_cooldown = 1.0 / self.shoot_rate
            self.last_shot_time = time.time()
    
    def take_damage(self, damage):
        """Recibe daño"""
        self.health -= damage
        
        # Efecto visual de daño
        self.flash_color = WHITE
        self.flash_timer = 0.1
        
        if self.health <= 0:
            self.on_death()
            
    def on_death(self):
        """Llamado cuando el enemigo muere"""
        # Efectos según el tipo
        if self.enemy_type == EnemyType.KAMIKAZE:
            # Explotar al morir
            if self.game:
                self.behavior_tree.blackboard["explosion_request"] = {
                    "position": self.pos.copy(),
                    "radius": 80,
                    "damage": 50
                }
        elif self.enemy_type == EnemyType.OFFICER:
            # Los oficiales pueden dejar power-ups
            if self.game and random.random() < 0.5:
                self.behavior_tree.blackboard["powerup_request"] = {
                    "position": self.pos.copy(),
                    "type": random.choice(["health", "ammo", "speed"])
                }
        
        # Eliminar del juego
        self.kill()
        print(f"{self.enemy_type} eliminado!")
    
    def update_sprite(self):
        """Actualiza el sprite según el estado"""
        # Por ahora solo cambiar color si hay flash
        if self.flash_color:
            self.image.fill(self.flash_color)
        else:
            self.image.fill(self.color)
            
        # TODO: Rotar sprite según ángulo cuando tengamos sprites reales
    
    def process_tree_requests(self, blackboard):
        """Procesa solicitudes del árbol de comportamiento"""
        # Verificar si hay solicitud de explosión
        if "explosion_request" in blackboard:
            if self.game:
                # TODO: Implementar en game
                print(f"Solicitud de explosión: {blackboard['explosion_request']}")
            del blackboard["explosion_request"]
            
        # Verificar si hay solicitud de refuerzos
        if "reinforcements_called" in blackboard and blackboard["reinforcements_called"]:
            if self.game:
                # TODO: Implementar spawn de refuerzos
                print(f"Solicitud de refuerzos en: {blackboard.get('reinforcements_position')}")
            blackboard["reinforcements_called"] = False
    
    def draw_debug(self, screen):
        """Dibuja información de debug"""
        # Dibujar path
        if self.path and len(self.path) > 1:
            points = []
            for x, y in self.path[self.path_index:]:
                world_x = x * TILE_SIZE + TILE_SIZE // 2
                world_y = y * TILE_SIZE + TILE_SIZE // 2
                points.append((world_x, world_y))
                
            if points:
                pygame.draw.lines(screen, YELLOW, False, points, 2)
        
        # Dibujar rango de visión
        pygame.draw.circle(screen, (255, 255, 0, 50), 
                          (int(self.pos.x), int(self.pos.y)), 
                          self.sight_range, 1)
        
        # Dibujar rango de disparo
        if self.shoot_range > 0:
            pygame.draw.circle(screen, (255, 0, 0, 30), 
                              (int(self.pos.x), int(self.pos.y)), 
                              self.shoot_range, 1)
        
        # Mostrar tipo de enemigo
        font = pygame.font.Font(None, 20)
        text = font.render(self.enemy_type, True, WHITE)
        text_rect = text.get_rect(center=(self.pos.x, self.pos.y - 25))
        screen.blit(text, text_rect)
        
        # Barra de vida
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 4
            bar_x = self.pos.x - bar_width // 2
            bar_y = self.pos.y - 35
            
            # Fondo
            pygame.draw.rect(screen, RED, 
                           (bar_x, bar_y, bar_width, bar_height))
            # Vida actual
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, GREEN, 
                           (bar_x, bar_y, health_width, bar_height))