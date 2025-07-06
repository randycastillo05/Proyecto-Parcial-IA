import pygame
import math
import os
from scripts.utils.enhance_sprites import EnhancedSprites
from scripts.utils.constants import *

class Player(pygame.sprite.Sprite):
    """Clase que representa al jugador con colisiones mejoradas"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Crear sprite mejorado
        self.load_enhanced_sprite()
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
        
        # Referencias al juego
        self.game = None
        self.grid = None  # Referencia al grid para colisiones
        
        # Estado del gamepad
        self.gamepad_shoot_held = False
        
        # Radio de colisión (más pequeño que el sprite para mejor gameplay)
        self.collision_radius = PLAYER_SIZE // 3
        
    def set_grid(self, grid):
        """Establece la referencia al grid para colisiones"""
        self.grid = grid
        
    def load_enhanced_sprite(self):
        """Carga el sprite mejorado o crea uno de respaldo"""
        sprite_path = os.path.join("assets", "images", "enhanced", "player.png")
        
        try:
            if os.path.exists(sprite_path):
                self.original_image = pygame.image.load(sprite_path).convert_alpha()
                print("✓ Sprite mejorado del jugador cargado")
            else:
                print("⚠ Generando sprite del jugador...")
                from scripts.utils.enhance_sprites import EnhancedSprites
                self.original_image = EnhancedSprites.create_detailed_player(48)
                
                os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                pygame.image.save(self.original_image, sprite_path)
                print("✓ Sprite del jugador generado y guardado")
                
        except Exception as e:
            print(f"❌ Error cargando sprite: {e}")
            self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.original_image.fill(GREEN)
            
        self.image = self.original_image.copy()
    
    def check_wall_collision(self, new_x, new_y):
        """Verifica si la nueva posición colisiona con muros"""
        if not self.grid:
            return False
            
        # Verificar múltiples puntos alrededor del jugador
        check_points = [
            (new_x, new_y),  # Centro
            (new_x - self.collision_radius, new_y),  # Izquierda
            (new_x + self.collision_radius, new_y),  # Derecha
            (new_x, new_y - self.collision_radius),  # Arriba
            (new_x, new_y + self.collision_radius),  # Abajo
            # Esquinas
            (new_x - self.collision_radius, new_y - self.collision_radius),
            (new_x + self.collision_radius, new_y - self.collision_radius),
            (new_x - self.collision_radius, new_y + self.collision_radius),
            (new_x + self.collision_radius, new_y + self.collision_radius),
        ]
        
        for check_x, check_y in check_points:
            # Convertir a coordenadas de grid
            grid_x = int(check_x // TILE_SIZE)
            grid_y = int(check_y // TILE_SIZE)
            
            # Verificar límites del mapa
            if (grid_x < 0 or grid_x >= self.grid.width or 
                grid_y < 0 or grid_y >= self.grid.height):
                return True  # Fuera del mapa = colisión
            
            # Verificar si la celda no es caminable
            node = self.grid.get_node(grid_x, grid_y)
            if node and not node.walkable:
                return True
                
        return False
    
    def handle_input(self, keys, mouse_pos, mouse_buttons, gamepad):
        """Maneja el input del jugador con verificación de colisiones"""
        # Resetear velocidad
        desired_velocity = pygame.math.Vector2(0, 0)
        
        # Input de gamepad si está disponible
        if gamepad:
            # Movimiento con stick izquierdo
            x_axis = gamepad.get_axis(0)
            y_axis = gamepad.get_axis(1)
            
            # Aplicar zona muerta
            if abs(x_axis) > 0.1:
                desired_velocity.x = x_axis * self.speed * self.speed_boost
            if abs(y_axis) > 0.1:
                desired_velocity.y = y_axis * self.speed * self.speed_boost
                
            # Apuntado con stick derecho
            aim_x = gamepad.get_axis(3)
            aim_y = gamepad.get_axis(4)
            
            if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
                self.angle = math.atan2(aim_y, aim_x)
            else:
                if desired_velocity.length() > 0:
                    self.angle = math.atan2(desired_velocity.y, desired_velocity.x)
                
            # Disparo con gatillo derecho
            trigger_value = gamepad.get_axis(5)
            if trigger_value > 0.5:
                if not self.gamepad_shoot_held:
                    self.is_shooting = True
                    self.gamepad_shoot_held = True
            else:
                self.gamepad_shoot_held = False
                self.is_shooting = False
                
        else:
            # Movimiento con teclado
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                desired_velocity.y = -self.speed * self.speed_boost
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                desired_velocity.y = self.speed * self.speed_boost
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                desired_velocity.x = -self.speed * self.speed_boost
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                desired_velocity.x = self.speed * self.speed_boost
                
            # Normalizar velocidad diagonal
            if desired_velocity.length() > 0:
                desired_velocity = desired_velocity.normalize() * self.speed * self.speed_boost
                
            # Apuntado con mouse
            dx = mouse_pos[0] - self.pos.x
            dy = mouse_pos[1] - self.pos.y
            self.angle = math.atan2(dy, dx)
            
            # Disparo con click izquierdo
            self.is_shooting = mouse_buttons[0]
        
        # Aplicar movimiento con verificación de colisiones
        self.apply_movement_with_collision(desired_velocity)
        
        # Procesar disparo
        if self.is_shooting and self.can_shoot:
            self.shoot()
    
    def apply_movement_with_collision(self, desired_velocity):
        """Aplica el movimiento verificando colisiones"""
        if desired_velocity.length() == 0:
            self.velocity = pygame.math.Vector2(0, 0)
            return
        
        # Intentar movimiento en X
        new_x = self.pos.x + desired_velocity.x * (1/60)  # Asumir 60 FPS para el cálculo
        if not self.check_wall_collision(new_x, self.pos.y):
            self.velocity.x = desired_velocity.x
        else:
            self.velocity.x = 0
            
        # Intentar movimiento en Y
        new_y = self.pos.y + desired_velocity.y * (1/60)
        if not self.check_wall_collision(self.pos.x, new_y):
            self.velocity.y = desired_velocity.y
        else:
            self.velocity.y = 0
            
        # Si no puede moverse en ambas direcciones, intentar movimiento diagonal
        if self.velocity.length() == 0 and desired_velocity.length() > 0:
            # Intentar movimiento diagonal completo
            if not self.check_wall_collision(new_x, new_y):
                self.velocity = desired_velocity
    
    def update(self, dt):
        """Actualiza el estado del jugador"""
        # Actualizar cooldown de disparo
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            self.can_shoot = False
        else:
            self.can_shoot = True
            
        # Actualizar timers de power-ups
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost = 1.0
                
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= dt
            if self.damage_boost_timer <= 0:
                self.damage_boost = 1.0
                
        if self.fire_rate_boost_timer > 0:
            self.fire_rate_boost_timer -= dt
            if self.fire_rate_boost_timer <= 0:
                self.fire_rate_boost = 1.0
        
        # Actualizar invulnerabilidad
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Actualizar efectos visuales
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_color = None
        
        # Aplicar movimiento con verificación final de colisiones
        new_pos = self.pos + self.velocity * dt
        
        # Verificación final de colisión antes de mover
        if not self.check_wall_collision(new_pos.x, new_pos.y):
            self.pos = new_pos
        else:
            # Si hay colisión, detener movimiento
            self.velocity = pygame.math.Vector2(0, 0)
        
        # Mantener dentro de la pantalla (límites absolutos)
        self.pos.x = max(self.collision_radius, min(SCREEN_WIDTH - self.collision_radius, self.pos.x))
        self.pos.y = max(self.collision_radius, min(SCREEN_HEIGHT - self.collision_radius, self.pos.y))
        
        # Actualizar rect
        self.rect.center = self.pos
        
        # Actualizar sprite con rotación
        self.update_sprite()
    
    def shoot(self):
        """Dispara un proyectil"""
        if self.can_shoot:
            self.shoot_request = True
            
            base_cooldown = SHOOT_COOLDOWN
            self.shoot_cooldown = base_cooldown / self.fire_rate_boost
            
            self.flash_color = (255, 255, 255)
            self.flash_timer = 0.08
    
    def take_damage(self, damage):
        """Recibe daño"""
        if self.invulnerable:
            return
            
        self.health -= damage
        self.health = max(0, self.health)
        
        self.flash_color = (255, 50, 50)
        self.flash_timer = 0.15
        
        self.invulnerable = True
        self.invulnerable_timer = 0.5
        
        if hasattr(self, 'game') and self.game and self.game.gamepad:
            try:
                self.game.gamepad.rumble(1.0, 1.0, 200)
            except:
                pass
                
        print(f"Jugador recibió {damage} de daño. Vida: {self.health}/{self.max_health}")
    
    def heal(self, amount):
        """Cura al jugador"""
        self.health = min(self.health + amount, self.max_health)
        self.flash_color = (100, 255, 100)
        self.flash_timer = 0.3
    
    def apply_speed_boost(self, multiplier, duration):
        """Aplica un boost de velocidad temporal"""
        self.speed_boost = multiplier
        self.speed_boost_timer = duration
        
    def apply_damage_boost(self, multiplier, duration):
        """Aplica un boost de daño temporal"""
        self.damage_boost = multiplier
        self.damage_boost_timer = duration
        
    def apply_fire_rate_boost(self, multiplier, duration):
        """Aplica un boost de velocidad de disparo temporal"""
        self.fire_rate_boost = multiplier
        self.fire_rate_boost_timer = duration
    
    def update_sprite(self):
        """Actualiza el sprite del jugador con rotación y efectos"""
        current_image = self.original_image.copy()
        
        # Aplicar efectos de color
        if self.flash_color:
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((*self.flash_color, 180))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        elif self.invulnerable:
            if int(self.invulnerable_timer * 15) % 2 == 0:
                overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Indicadores de power-ups
        if self.speed_boost > 1.0:
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 200, 255, 80))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        if self.damage_boost > 1.0:
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 100, 0, 80))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
        if self.fire_rate_boost > 1.0:
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 80))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Rotar sprite según ángulo
        if self.angle != 0:
            angle_degrees = -math.degrees(self.angle)
            rotated_image = pygame.transform.rotate(current_image, angle_degrees)        
            old_center = self.rect.center
            self.image = rotated_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        else:
            self.image = current_image
    
    def get_damage(self):
        """Retorna el daño actual con boosts aplicados"""
        return BULLET_DAMAGE * self.damage_boost
    
    def draw_debug_info(self, screen):
        """Dibuja información de debug sobre el jugador"""
        if hasattr(self, 'game') and self.game and self.game.show_debug_info:
            # Círculo de colisión
            pygame.draw.circle(screen, (0, 255, 0), 
                             (int(self.pos.x), int(self.pos.y)), 
                             self.collision_radius, 1)
            
            # Línea de apuntado
            end_x = self.pos.x + math.cos(self.angle) * 100
            end_y = self.pos.y + math.sin(self.angle) * 100
            pygame.draw.line(screen, (255, 255, 0), 
                           (self.pos.x, self.pos.y), (end_x, end_y), 2)