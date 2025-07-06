import pygame
import math
import time
import random
import os
from scripts.utils.constants import *
from scripts.ai.behavior_tree import BehaviorTree
from scripts.ai.enemy_behaviors import EnemyBehaviorFactory

class Enemy(pygame.sprite.Sprite):
    """Clase base para todos los enemigos con árbol de comportamiento y sprites mejorados"""
    
    def __init__(self, x, y, enemy_type=EnemyType.SOLDIER):
        super().__init__()
        
        # Configuración según tipo de enemigo
        self.enemy_type = enemy_type
        self.setup_enemy_stats()
        
        # Cargar sprite mejorado
        self.load_enhanced_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Posición y movimiento
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.facing_direction = 0  # Para voltear el sprite
        
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
        self.hurt_timer = 0
        
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
        
        # Animación
        self.animation_timer = 0
        self.bob_offset = 0
        
    def load_enhanced_sprite(self):
        """Carga el sprite mejorado del enemigo"""
        sprite_filename = f"enemy_{self.enemy_type}.png"
        sprite_path = os.path.join("assets", "images", "enhanced", sprite_filename)
        
        try:
            # Intentar cargar sprite mejorado
            if os.path.exists(sprite_path):
                self.original_image = pygame.image.load(sprite_path).convert_alpha()
                print(f"✓ Sprite mejorado de {self.enemy_type} cargado")
            else:
                # Generar sprite si no existe
                print(f"⚠ Generando sprite de {self.enemy_type}...")
                from ikari_warriors_RC.scripts.utils.enhance_sprites import EnhancedSprites
                
                # Generar sprite según tipo
                if self.enemy_type == EnemyType.SOLDIER:
                    self.original_image = EnhancedSprites.create_detailed_soldier()
                elif self.enemy_type == EnemyType.ELITE:
                    self.original_image = EnhancedSprites.create_detailed_elite()
                elif self.enemy_type == EnemyType.SNIPER:
                    self.original_image = EnhancedSprites.create_detailed_sniper()
                elif self.enemy_type == EnemyType.KAMIKAZE:
                    self.original_image = EnhancedSprites.create_detailed_kamikaze()
                elif self.enemy_type == EnemyType.OFFICER:
                    self.original_image = EnhancedSprites.create_detailed_officer()
                else:
                    self.original_image = EnhancedSprites.create_detailed_soldier()
                
                # Guardar para uso futuro
                os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                pygame.image.save(self.original_image, sprite_path)
                print(f"✓ Sprite de {self.enemy_type} generado y guardado")
                
        except Exception as e:
            print(f"❌ Error cargando sprite de {self.enemy_type}: {e}")
            # Fallback al sprite original
            self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.original_image.fill(self.color)
            
        self.image = self.original_image.copy()
        
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
            self.score_value = 100
            
        elif self.enemy_type == EnemyType.ELITE:
            self.max_health = 75
            self.speed = 120
            self.sight_range = 250
            self.shoot_range = 180
            self.shoot_rate = 0.8
            self.accuracy = 0.85
            self.color = (139, 0, 0)  # Rojo oscuro
            self.score_value = 200
            
        elif self.enemy_type == EnemyType.SNIPER:
            self.max_health = 40
            self.speed = 80
            self.sight_range = 400
            self.shoot_range = 350
            self.shoot_rate = 0.3
            self.accuracy = 0.95
            self.color = (128, 0, 128)  # Púrpura
            self.score_value = 300
            
        elif self.enemy_type == EnemyType.KAMIKAZE:
            self.max_health = 30
            self.speed = 180
            self.sight_range = 150
            self.shoot_range = 0  # No dispara
            self.shoot_rate = 0
            self.accuracy = 0
            self.color = (255, 165, 0)  # Naranja
            self.score_value = 150
            
        elif self.enemy_type == EnemyType.OFFICER:
            self.max_health = 100
            self.speed = 90
            self.sight_range = 200
            self.shoot_range = 120
            self.shoot_rate = 0.4
            self.accuracy = 0.6
            self.color = (0, 100, 0)  # Verde oscuro
            self.score_value = 500
    
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
            self.patrol_points = []
            for dx, dy in offsets:
                patrol_x = center_x + dx
                patrol_y = center_y + dy
                patrol_x = max(50, min(SCREEN_WIDTH - 50, patrol_x))
                patrol_y = max(50, min(SCREEN_HEIGHT - 50, patrol_y))
                self.patrol_points.append((patrol_x, patrol_y))
        else:
            # Patrulla normal
            offsets = [(100, 0), (0, 100), (-100, 0), (0, -100)]
            self.patrol_points = []
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
        self.animation_timer += dt
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            self.can_shoot = False
        else:
            self.can_shoot = True
            
        # Actualizar efectos visuales
        if self.flash_timer > 0:
            self.flash_timer -= dt
        
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        
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
        
        # Animación de movimiento (bobbing)
        if self.velocity.length() > 0:
            self.bob_offset = math.sin(self.animation_timer * 10) * 2
        else:
            self.bob_offset *= 0.9  # Suavizar cuando se detiene
        
        # Actualizar sprite según ángulo y estado
        self.update_sprite()
    
    def can_see_player(self):
        """Verifica si puede ver al jugador con línea de visión"""
        if not self.player:
            return False
            
        distance = self.pos.distance_to(self.player.pos)
        
        if distance <= self.sight_range:
            # Verificar línea de visión con raycasting simple
            if self.pathfinder and self.pathfinder.grid:
                # Puntos a verificar en la línea
                steps = int(distance / TILE_SIZE)
                if steps > 0:
                    for i in range(steps):
                        t = i / steps
                        check_x = self.pos.x + (self.player.pos.x - self.pos.x) * t
                        check_y = self.pos.y + (self.player.pos.y - self.pos.y) * t
                        
                        node = self.pathfinder.grid.get_node_from_world_pos(check_x, check_y)
                        if node and not node.walkable:
                            return False  # Hay un obstáculo bloqueando la vista
                            
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
            
            # Calcular dispersión según precisión
            spread = (1.0 - actual_accuracy) * 0.5
            angle_offset = random.uniform(-spread, spread)
            
            # Para el francotirador, añadir láser de apuntado
            if self.enemy_type == EnemyType.SNIPER:
                self.show_sniper_laser = True
            
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
        """Recibe daño con efectos mejorados"""
        self.health -= damage
        
        # Efectos visuales de daño
        self.flash_color = WHITE
        self.flash_timer = 0.1
        self.hurt_timer = 0.3
        
        # Efecto de retroceso
        if self.player:
            knockback_dir = self.pos - self.player.pos
            if knockback_dir.length() > 0:
                knockback_dir = knockback_dir.normalize()
                self.pos += knockback_dir * 10
        
        # Partículas de sangre
        if self.game:
            impact_angle = math.atan2(self.player.pos.y - self.pos.y, 
                                    self.player.pos.x - self.pos.x)
            self.game.particle_system.create_blood_splatter(
                self.pos.x, self.pos.y, impact_angle + math.pi
            )
        
        if self.health <= 0:
            self.on_death()
            
    def on_death(self):
        """Llamado cuando el enemigo muere con efectos mejorados"""
        # Dar puntos al jugador
        if self.game:
            self.game.score += self.score_value
            
            # Verificar combo
            if hasattr(self.game, 'combo_system'):
                self.game.combo_system.add_kill()
        
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
        else:
            # Chance normal de power-up
            if self.game and random.random() < 0.15:
                self.behavior_tree.blackboard["powerup_request"] = {
                    "position": self.pos.copy(),
                    "type": random.choice(["health", "ammo", "speed"])
                }
        
        # Partículas de muerte
        if self.game:
            self.game.particle_system.create_explosion(
                self.pos.x, self.pos.y, 0.5
            )
        
        # Eliminar del juego
        self.kill()
        print(f"{self.enemy_type} eliminado! +{self.score_value} puntos")
    
    def update_sprite(self):
        """Actualiza el sprite con rotación y efectos"""
        # Comenzar con la imagen original
        current_image = self.original_image.copy()
        
        # Aplicar efectos de color
        if self.flash_timer > 0:
            # Flash de daño
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
        elif self.hurt_timer > 0:
            # Tinte rojo cuando está herido
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 100))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # Indicador de buff (aura)
        if self.speed_buff > 1.0 or self.accuracy_buff > 1.0 or self.damage_buff > 1.0:
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 215, 0, 50))  # Aura dorada
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Efecto especial para kamikaze
        if self.enemy_type == EnemyType.KAMIKAZE and self.player:
            distance = self.pos.distance_to(self.player.pos)
            if distance < 100:
                # Parpadeo rojo cuando está cerca
                if int(self.animation_timer * 10) % 2 == 0:
                    overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, 150))
                    current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Rotar sprite según ángulo
        if self.velocity.length() > 0:
            # Voltear horizontalmente si mira a la izquierda
            if abs(self.angle) > math.pi/2:
                current_image = pygame.transform.flip(current_image, True, False)
        
        # Aplicar bobbing vertical
        self.image = current_image
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (old_center[0], old_center[1] + self.bob_offset)
    
    def process_tree_requests(self, blackboard):
        """Procesa solicitudes del árbol de comportamiento"""
        # Verificar si hay solicitud de explosión
        if "explosion_request" in blackboard:
            if self.game:
                req = blackboard["explosion_request"]
                self.game.create_explosion(req["position"].x, req["position"].y, 
                                         req["radius"], req["damage"])
            del blackboard["explosion_request"]
            
        # Verificar si hay solicitud de refuerzos
        if "reinforcements_called" in blackboard and blackboard["reinforcements_called"]:
            if self.game:
                # Implementar spawn de refuerzos
                reinforcement_pos = blackboard.get('reinforcements_position', self.pos)
                # Generar 2-3 soldados cerca
                for i in range(random.randint(2, 3)):
                    spawn_angle = random.uniform(0, math.pi * 2)
                    spawn_distance = random.uniform(100, 150)
                    spawn_x = reinforcement_pos[0] + math.cos(spawn_angle) * spawn_distance
                    spawn_y = reinforcement_pos[1] + math.sin(spawn_angle) * spawn_distance
                    
                    # Mantener dentro de la pantalla
                    spawn_x = max(50, min(SCREEN_WIDTH - 50, spawn_x))
                    spawn_y = max(50, min(SCREEN_HEIGHT - 50, spawn_y))
                    
                    self.game.spawn_enemy(spawn_x, spawn_y, EnemyType.SOLDIER)
                
                print(f"¡Refuerzos llamados por {self.enemy_type}!")
            blackboard["reinforcements_called"] = False
    
    def draw_debug(self, screen):
        """Dibuja información de debug mejorada"""
        # Dibujar path
        if self.path and len(self.path) > 1:
            points = []
            for x, y in self.path[self.path_index:]:
                world_x = x * TILE_SIZE + TILE_SIZE // 2
                world_y = y * TILE_SIZE + TILE_SIZE // 2
                points.append((world_x, world_y))
                
            if len(points) >= 2:
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
        
        # Láser del francotirador
        if self.enemy_type == EnemyType.SNIPER and self.player and self.can_see_player():
            # Línea de apuntado con puntos
            for i in range(0, int(self.pos.distance_to(self.player.pos)), 20):
                t = i / self.pos.distance_to(self.player.pos)
                dot_x = self.pos.x + (self.player.pos.x - self.pos.x) * t
                dot_y = self.pos.y + (self.player.pos.y - self.pos.y) * t
                pygame.draw.circle(screen, (255, 0, 0), (int(dot_x), int(dot_y)), 2)
        
        # Mostrar tipo de enemigo
        font = pygame.font.Font(None, 20)
        text = font.render(self.enemy_type, True, WHITE)
        text_rect = text.get_rect(center=(self.pos.x, self.pos.y - 35))
        screen.blit(text, text_rect)
        
        # Barra de vida mejorada
        if self.health < self.max_health:
            from scripts.utils.enhanced_visual import VisualEffects
            VisualEffects.draw_health_bar(
                screen, 
                self.pos.x - 20, 
                self.pos.y - 45,
                40, 4,
                self.health, self.max_health,
                (0, 255, 0), (100, 0, 0)
            )
        
        # Mostrar buffs activos
        if self.speed_buff > 1.0 or self.accuracy_buff > 1.0 or self.damage_buff > 1.0:
            buff_text = f"↑"
            if self.speed_buff > 1.0:
                buff_text += "S"
            if self.accuracy_buff > 1.0:
                buff_text += "A"
            if self.damage_buff > 1.0:
                buff_text += "D"
            
            buff_surface = font.render(buff_text, True, (255, 215, 0))
            buff_rect = buff_surface.get_rect(center=(self.pos.x + 25, self.pos.y - 25))
            screen.blit(buff_surface, buff_rect)