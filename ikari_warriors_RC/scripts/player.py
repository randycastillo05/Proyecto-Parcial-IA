import pygame
import math
import os
from scripts.utils.constants import *

class Player(pygame.sprite.Sprite):
    """Clase que representa al jugador con sprites mejorados"""
    
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
        
        # Referencia al juego
        self.game = None
        
        # Estado del gamepad
        self.gamepad_shoot_held = False
        
    def load_enhanced_sprite(self):
        """Carga el sprite mejorado o crea uno de respaldo"""
        sprite_path = os.path.join("assets", "images", "enhanced", "player.png")
        
        try:
            # Intentar cargar sprite mejorado
            if os.path.exists(sprite_path):
                self.original_image = pygame.image.load(sprite_path).convert_alpha()
                print("✓ Sprite mejorado del jugador cargado")
            else:
                # Generar sprite si no existe
                print("⚠ Generando sprite del jugador...")
                from enhance_sprites import EnhancedSprites
                self.original_image = EnhancedSprites.create_detailed_player(48)
                
                # Guardar para uso futuro
                os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                pygame.image.save(self.original_image, sprite_path)
                print("✓ Sprite del jugador generado y guardado")
                
        except Exception as e:
            print(f"❌ Error cargando sprite: {e}")
            # Fallback al sprite original
            self.original_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.original_image.fill(GREEN)
            
        self.image = self.original_image.copy()
        
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
            if abs(y_axis) > 0.1:
                self.velocity.y = y_axis * self.speed * self.speed_boost
                
            # Apuntado con stick derecho
            aim_x = gamepad.get_axis(3)  # Eje X del stick derecho
            aim_y = gamepad.get_axis(4)  # Eje Y del stick derecho
            
            if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
                self.angle = math.atan2(aim_y, aim_x)
            else:
                # Si no se está apuntando, usar la dirección de movimiento
                if self.velocity.length() > 0:
                    self.angle = math.atan2(self.velocity.y, self.velocity.x)
                
            # Disparo con gatillo derecho (RT/R2)
            trigger_value = gamepad.get_axis(5)
            if trigger_value > 0.5:
                if not self.gamepad_shoot_held:
                    self.is_shooting = True
                    self.gamepad_shoot_held = True
            else:
                self.gamepad_shoot_held = False
                self.is_shooting = False
                
            # Botones adicionales
            if gamepad.get_button(0):  # A/X
                # TODO: Acción especial (granada, dash, etc.)
                pass
                
        else:
            # Movimiento con teclado
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.velocity.y = -self.speed * self.speed_boost
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.velocity.y = self.speed * self.speed_boost
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velocity.x = -self.speed * self.speed_boost
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velocity.x = self.speed * self.speed_boost
                
            # Normalizar velocidad diagonal
            if self.velocity.length() > 0:
                self.velocity = self.velocity.normalize() * self.speed * self.speed_boost
                
            # Apuntado con mouse
            dx = mouse_pos[0] - self.pos.x
            dy = mouse_pos[1] - self.pos.y
            self.angle = math.atan2(dy, dx)
            
            # Disparo con click izquierdo
            self.is_shooting = mouse_buttons[0]
        
        # Procesar disparo
        if self.is_shooting and self.can_shoot:
            self.shoot()
    
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
        
        # Mover jugador
        self.pos += self.velocity * dt
        
        # Mantener dentro de la pantalla
        self.pos.x = max(PLAYER_SIZE//2, min(SCREEN_WIDTH - PLAYER_SIZE//2, self.pos.x))
        self.pos.y = max(PLAYER_SIZE//2, min(SCREEN_HEIGHT - PLAYER_SIZE//2, self.pos.y))
        
        # Actualizar rect
        self.rect.center = self.pos
        
        # Actualizar sprite con rotación
        self.update_sprite()
        
    def shoot(self):
        """Dispara un proyectil"""
        if self.can_shoot:
            # Marcar solicitud de disparo para que Game la procese
            self.shoot_request = True
            
            # Aplicar cooldown con boost de fire rate
            base_cooldown = SHOOT_COOLDOWN
            self.shoot_cooldown = base_cooldown / self.fire_rate_boost
            
            # Efecto visual mejorado
            self.flash_color = (255, 255, 255)
            self.flash_timer = 0.08
            
    def take_damage(self, damage):
        """Recibe daño"""
        if self.invulnerable:
            return
            
        self.health -= damage
        self.health = max(0, self.health)
        
        # Efecto visual de daño más intenso
        self.flash_color = (255, 50, 50)
        self.flash_timer = 0.15
        
        # Breve invulnerabilidad después del daño
        self.invulnerable = True
        self.invulnerable_timer = 0.5
        
        # Vibración del gamepad si está disponible
        if hasattr(self, 'game') and self.game and self.game.gamepad:
            try:
                self.game.gamepad.rumble(1.0, 1.0, 200)  # Vibración fuerte por 200ms
            except:
                pass  # No todos los gamepads soportan vibración
                
        print(f"Jugador recibió {damage} de daño. Vida: {self.health}/{self.max_health}")
    
    def heal(self, amount):
        """Cura al jugador"""
        self.health = min(self.health + amount, self.max_health)
        
        # Efecto visual de curación mejorado
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
        # Comenzar con la imagen original
        current_image = self.original_image.copy()
        
        # Aplicar efectos de color
        if self.flash_color:
            # Crear overlay de color
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((*self.flash_color, 180))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
        elif self.invulnerable:
            # Parpadeo cuando es invulnerable
            if int(self.invulnerable_timer * 15) % 2 == 0:
                overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Indicadores visuales de power-ups
        if self.speed_boost > 1.0:
            # Aura azul para velocidad
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 100, 255, 50))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
        if self.damage_boost > 1.0:
            # Aura roja para daño
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 100, 0, 50))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
        if self.fire_rate_boost > 1.0:
            # Aura amarilla para velocidad de disparo
            overlay = pygame.Surface(current_image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 50))
            current_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Rotar sprite según ángulo de apuntado
        if self.angle != 0:
            # Convertir ángulo a grados y rotar
            angle_degrees = -math.degrees(self.angle)
            rotated_image = pygame.transform.rotate(current_image, angle_degrees)
            
            # Mantener el centro
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
            # Círculo de detección
            pygame.draw.circle(screen, (0, 255, 0, 50), 
                             (int(self.pos.x), int(self.pos.y)), 
                             PLAYER_SIZE, 1)
            
            # Línea de apuntado
            end_x = self.pos.x + math.cos(self.angle) * 100
            end_y = self.pos.y + math.sin(self.angle) * 100
            pygame.draw.line(screen, (255, 255, 0), 
                           (self.pos.x, self.pos.y), (end_x, end_y), 2)
            
            # Información de estado
            font = pygame.font.Font(None, 24)
            info_texts = [
                f"Vida: {self.health}/{self.max_health}",
                f"Vel: {self.speed_boost:.1f}x",
                f"Daño: {self.damage_boost:.1f}x",
                f"Disparo: {self.fire_rate_boost:.1f}x",
                f"Ángulo: {math.degrees(self.angle):.1f}°"
            ]
            
            for i, text in enumerate(info_texts):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 150 + i * 25))