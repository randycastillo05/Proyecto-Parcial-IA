import pygame
import math
import os
from scripts.utils.constants import *
from scripts.utils.enhance_sprites import EnhancedSprites

class Bullet(pygame.sprite.Sprite):
    """Clase para los proyectiles del juego con sprites mejorados"""
    
    def __init__(self, x, y, angle, damage=BULLET_DAMAGE, speed=BULLET_SPEED, owner=None):
        super().__init__()
        
        # Cargar sprite mejorado
        self.load_enhanced_sprite()
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
        
        # Trail effect mejorado
        self.trail_positions = []
        self.max_trail_length = 8
        
        # Rotar sprite según ángulo
        self.rotate_sprite()
        
    def load_enhanced_sprite(self):
        """Carga el sprite mejorado de la bala"""
        sprite_path = os.path.join("assets", "images", "enhanced", "bullet.png")
        
        try:
            # Intentar cargar sprite mejorado
            if os.path.exists(sprite_path):
                self.original_image = pygame.image.load(sprite_path).convert_alpha()
                print("✓ Sprite mejorado de bala cargado")
            else:
                # Generar sprite si no existe
                print("⚠ Generando sprite de bala...")
                from ikari_warriors_RC.scripts.utils.enhance_sprites import EnhancedSprites
                self.original_image = EnhancedSprites.create_detailed_bullet(12)
                
                # Guardar para uso futuro
                os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                pygame.image.save(self.original_image, sprite_path)
                print("✓ Sprite de bala generado y guardado")
                
        except Exception as e:
            print(f"❌ Error cargando sprite de bala: {e}")
            # Fallback al sprite original
            self.original_image = pygame.Surface((6, 6))
            self.original_image.fill(YELLOW)
            
        self.image = self.original_image.copy()
    
    def rotate_sprite(self):
        """Rota el sprite según el ángulo de movimiento"""
        if hasattr(self, 'original_image'):
            angle_degrees = -math.degrees(self.angle)
            self.image = pygame.transform.rotate(self.original_image, angle_degrees)
            
            # Mantener el centro
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
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
        """Dibuja el trail mejorado de la bala"""
        if len(self.trail_positions) > 1:
            for i in range(1, len(self.trail_positions)):
                # Calcular alpha degradado
                alpha = int((i / len(self.trail_positions)) * 255)
                
                # Colores del trail según el owner
                if hasattr(self.owner, 'enemy_type'):
                    # Bala de enemigo - trail rojo
                    base_color = (255, 100, 100)
                else:
                    # Bala de jugador - trail amarillo/dorado
                    base_color = (255, 255, 100)
                
                # Crear superficie temporal para alpha
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                trail_color = (*base_color, alpha)
                pygame.draw.circle(trail_surface, trail_color, (2, 2), 2)
                
                # Dibujar trail
                trail_pos = self.trail_positions[i]
                screen.blit(trail_surface, (trail_pos.x - 2, trail_pos.y - 2))


class Explosion(pygame.sprite.Sprite):
    """Efecto de explosión mejorado con sprites animados"""
    
    def __init__(self, x, y, radius=50, damage=50, duration=0.5):
        super().__init__()
        
        self.pos = pygame.math.Vector2(x, y)
        self.radius = radius
        self.max_radius = radius
        self.damage = damage
        self.duration = duration
        self.elapsed = 0
        self.has_damaged = False
        
        # Cargar frames de animación
        self.load_explosion_frames()
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = duration / len(self.explosion_frames) if self.explosion_frames else 0.1
        
        # Sprite temporal inicial
        if self.explosion_frames:
            self.image = self.explosion_frames[0]
        else:
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def load_explosion_frames(self):
        """Carga los frames de animación de explosión"""
        self.explosion_frames = []
        
        for i in range(8):  # 8 frames de animación
            frame_path = os.path.join("assets", "images", "enhanced", f"explosion_{i}.png")
            
            try:
                if os.path.exists(frame_path):
                    frame = pygame.image.load(frame_path).convert_alpha()
                    # Escalar según el tamaño de la explosión
                    scale_factor = self.max_radius / 32  # 32 es el tamaño base
                    new_size = (int(64 * scale_factor), int(64 * scale_factor))
                    frame = pygame.transform.scale(frame, new_size)
                    self.explosion_frames.append(frame)
                else:
                    # Generar frame si no existe
                    from ikari_warriors_RC.scripts.utils.enhance_sprites import EnhancedSprites
                    frames = EnhancedSprites.create_explosion_animation(8, self.max_radius * 2)
                    self.explosion_frames = frames
                    
                    # Guardar frames generados
                    os.makedirs(os.path.dirname(frame_path), exist_ok=True)
                    for j, generated_frame in enumerate(frames):
                        save_path = os.path.join("assets", "images", "enhanced", f"explosion_{j}.png")
                        pygame.image.save(generated_frame, save_path)
                    break
                    
            except Exception as e:
                print(f"❌ Error cargando frame de explosión {i}: {e}")
                # Crear frame básico
                frame = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(frame, (255, 200, 0), 
                                 (self.max_radius, self.max_radius), 
                                 self.max_radius - i * 5)
                self.explosion_frames.append(frame)
        
        if not self.explosion_frames:
            # Fallback: crear un frame básico
            frame = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(frame, (255, 200, 0), 
                             (self.max_radius, self.max_radius), self.max_radius)
            self.explosion_frames.append(frame)
        
    def update(self, dt):
        """Actualiza la explosión con animación"""
        self.elapsed += dt
        self.frame_timer += dt
        
        # Calcular progreso (0 a 1)
        progress = self.elapsed / self.duration
        
        if progress >= 1.0:
            self.kill()
            return
        
        # Actualizar frame de animación
        if self.frame_timer >= self.frame_duration and self.explosion_frames:
            self.current_frame = min(self.current_frame + 1, len(self.explosion_frames) - 1)
            self.frame_timer = 0
            
            # Actualizar imagen
            self.image = self.explosion_frames[self.current_frame]
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # Expandir radius para colisión
        if progress < 0.3:
            # Fase de expansión
            self.radius = self.max_radius * (progress / 0.3)
        else:
            # Fase de desvanecimiento
            self.radius = self.max_radius
    
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
    """Power-ups mejorados con sprites detallados"""
    
    def __init__(self, x, y, powerup_type="health"):
        super().__init__()
        
        self.powerup_type = powerup_type
        self.pos = pygame.math.Vector2(x, y)
        
        # Configurar según tipo
        if powerup_type == "health":
            self.value = 25
        elif powerup_type == "ammo":
            self.value = 50
        elif powerup_type == "speed":
            self.value = 1.5  # Multiplicador
            self.duration = 5.0  # Segundos
        else:
            self.value = 0
        
        # Cargar sprite mejorado
        self.load_enhanced_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Animación
        self.bob_offset = 0
        self.bob_speed = 2
        self.rotation_angle = 0
        self.rotation_speed = 60  # Grados por segundo
        self.lifetime = 10.0  # Desaparece después de 10 segundos
        self.flash_timer = 0
        
        # Efectos de partículas
        self.particle_timer = 0
        self.particle_interval = 0.2
        
    def load_enhanced_sprite(self):
        """Carga el sprite mejorado del power-up"""
        sprite_filename = f"powerup_{self.powerup_type}.png"
        sprite_path = os.path.join("assets", "images", "enhanced", sprite_filename)
        
        try:
            # Intentar cargar sprite mejorado
            if os.path.exists(sprite_path):
                self.original_image = pygame.image.load(sprite_path).convert_alpha()
                print(f"✓ Sprite mejorado de power-up {self.powerup_type} cargado")
            else:
                # Generar sprite si no existe
                print(f"⚠ Generando sprite de power-up {self.powerup_type}...")
                from ikari_warriors_RC.scripts.utils.enhance_sprites import EnhancedSprites
                self.original_image = EnhancedSprites.create_detailed_powerup(self.powerup_type, 32)
                
                # Guardar para uso futuro
                os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                pygame.image.save(self.original_image, sprite_path)
                print(f"✓ Sprite de power-up {self.powerup_type} generado y guardado")
                
        except Exception as e:
            print(f"❌ Error cargando sprite de power-up {self.powerup_type}: {e}")
            # Fallback al sprite original
            color_map = {
                "health": GREEN,
                "ammo": YELLOW,
                "speed": BLUE
            }
            color = color_map.get(self.powerup_type, WHITE)
            
            self.original_image = pygame.Surface((20, 20))
            self.original_image.fill(color)
            
        self.image = self.original_image.copy()
    
    def update(self, dt):
        """Actualiza el power-up con animaciones mejoradas"""
        # Animación de flotación
        self.bob_offset += self.bob_speed * dt
        bob_y = math.sin(self.bob_offset) * 8
        
        # Animación de rotación
        self.rotation_angle += self.rotation_speed * dt
        if self.rotation_angle >= 360:
            self.rotation_angle -= 360
        
        # Actualizar posición Y con flotación
        self.rect.centery = self.pos.y + bob_y
        
        # Rotar sprite
        rotated_image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        old_center = self.rect.center
        self.image = rotated_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        
        # Actualizar lifetime
        self.lifetime -= dt
        
        # Efecto de parpadeo cuando queda poco tiempo
        if self.lifetime < 3.0:
            self.flash_timer += dt
            if self.flash_timer > 0.3:
                self.flash_timer = 0
                # Alternar alpha
                current_alpha = self.image.get_alpha()
                if current_alpha is None or current_alpha == 255:
                    self.image.set_alpha(128)
                else:
                    self.image.set_alpha(255)
        
        # Timer de partículas
        self.particle_timer += dt
        
        # Eliminar si expira
        if self.lifetime <= 0:
            self.kill()
    
    def apply_to_player(self, player):
        """Aplica el efecto al jugador con efectos mejorados"""
        if self.powerup_type == "health":
            old_health = player.health
            player.health = min(player.health + self.value, player.max_health)
            actual_heal = player.health - old_health
            print(f"¡Vida +{actual_heal}! ({player.health}/{player.max_health})")
            
        elif self.powerup_type == "ammo":
            # TODO: Implementar munición cuando tengamos sistema de armas
            print(f"¡Munición +{self.value}!")
            
        elif self.powerup_type == "speed":
            player.apply_speed_boost(self.value, self.duration)
            print(f"¡Velocidad x{self.value} por {self.duration}s!")
        
        # Efecto de sonido
        # TODO: Reproducir sonido de power-up
        
        self.kill()
    
    def draw_particles(self, screen):
        """Dibuja partículas alrededor del power-up"""
        if self.particle_timer >= self.particle_interval:
            # Crear partículas según el tipo
            particle_colors = {
                "health": [(0, 255, 0), (100, 255, 100), (200, 255, 200)],
                "ammo": [(255, 255, 0), (255, 200, 0), (255, 150, 0)],
                "speed": [(0, 100, 255), (100, 150, 255), (200, 220, 255)]
            }
            
            colors = particle_colors.get(self.powerup_type, [(255, 255, 255)])
            
            # Dibujar pequeñas partículas giratorias
            for i in range(6):
                angle = (i / 6) * 2 * math.pi + self.rotation_angle * 0.01
                radius = 25 + math.sin(self.bob_offset + i) * 5
                
                particle_x = self.rect.centerx + math.cos(angle) * radius
                particle_y = self.rect.centery + math.sin(angle) * radius
                
                color = colors[i % len(colors)]
                pygame.draw.circle(screen, color, (int(particle_x), int(particle_y)), 2)


class BulletManager:
    """Gestiona todos los proyectiles del juego con sprites mejorados"""
    
    def __init__(self, bullet_group, explosion_group):
        self.bullets = bullet_group
        self.explosions = explosion_group
        self.bullet_pool = []  # Para reutilizar objetos
        
    def create_bullet(self, x, y, angle, damage=BULLET_DAMAGE, 
                     speed=BULLET_SPEED, owner=None):
        """Crea una nueva bala mejorada"""
        bullet = Bullet(x, y, angle, damage, speed, owner)
        self.bullets.add(bullet)
        return bullet
    
    def create_explosion(self, x, y, radius=50, damage=50):
        """Crea una explosión mejorada"""
        explosion = Explosion(x, y, radius, damage)
        self.explosions.add(explosion)
        return explosion
    
    def update(self, dt):
        """Actualiza todos los proyectiles"""
        # Las balas y explosiones se actualizan automáticamente por los grupos
        pass
    
    def check_bullet_collisions(self, targets, obstacles=None):
        """Verifica colisiones de balas con objetivos"""
        hits = {}
        
        for bullet in self.bullets:
            # Colisión con objetivos
            for target in targets:
                if bullet.owner != target and bullet.rect.colliderect(target.rect):
                    if target not in hits:
                        hits[target] = []
                    hits[target].append(bullet)
                    bullet.kill()
                    break
            
            # Colisión con obstáculos
            if obstacles and bullet.alive():
                # Convertir posición de bala a coordenadas de grid
                grid_x = int(bullet.pos.x // TILE_SIZE)
                grid_y = int(bullet.pos.y // TILE_SIZE)
                
                # Verificar si está en un obstáculo
                if obstacles.get_node(grid_x, grid_y):
                    node = obstacles.get_node(grid_x, grid_y)
                    if not node.walkable:
                        bullet.kill()
                        # Crear pequeña chispa
                        self.create_explosion(bullet.pos.x, bullet.pos.y, 10, 0)
        
        return hits
    
    def check_explosion_damage(self, targets):
        """Verifica daño de explosiones"""
        for explosion in self.explosions:
            if not explosion.has_damaged:
                for target in targets:
                    explosion.check_damage(target)
                explosion.has_damaged = True
    
    def draw_trails(self, screen):
        """Dibuja los trails mejorados de las balas"""
        for bullet in self.bullets:
            bullet.draw_trail(screen)
    
    def draw_powerup_particles(self, screen, powerups):
        """Dibuja partículas de power-ups"""
        for powerup in powerups:
            if hasattr(powerup, 'draw_particles'):
                powerup.draw_particles(screen)