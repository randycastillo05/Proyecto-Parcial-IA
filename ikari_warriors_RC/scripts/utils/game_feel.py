import pygame
import math
import random

from scripts.utils.enhanced_visual import VisualEffects

class CameraSystem:
    """Sistema de cámara con efectos suaves"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.shake_amount = 0
        self.shake_duration = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # Suavizado
        self.smoothing = 0.1
        self.zoom_smoothing = 0.05
        
    def follow(self, target_pos, lead_amount=0.3):
        """Sigue al objetivo con suavizado y anticipación"""
        # Calcular posición objetivo con anticipación
        if hasattr(target_pos, 'velocity'):
            self.target_x = target_pos.x + target_pos.velocity.x * lead_amount
            self.target_y = target_pos.y + target_pos.velocity.y * lead_amount
        else:
            self.target_x = target_pos[0]
            self.target_y = target_pos[1]
        
        # Centrar en pantalla
        self.target_x -= self.width // 2
        self.target_y -= self.height // 2
    
    def update(self, dt):
        """Actualiza la posición de la cámara"""
        # Suavizar movimiento
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Suavizar zoom
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_smoothing
        
        # Actualizar shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            shake_x = random.randint(-self.shake_amount, self.shake_amount)
            shake_y = random.randint(-self.shake_amount, self.shake_amount)
            self.x += shake_x
            self.y += shake_y
    
    def shake(self, amount, duration):
        """Añade temblor a la cámara"""
        self.shake_amount = amount
        self.shake_duration = duration
    
    def set_zoom(self, zoom, instant=False):
        """Establece el nivel de zoom"""
        self.target_zoom = max(0.5, min(2.0, zoom))
        if instant:
            self.zoom = self.target_zoom
    
    def apply(self, surface, target_surface):
        """Aplica la transformación de cámara"""
        # Crear superficie temporal si hay zoom
        if self.zoom != 1.0:
            scaled_size = (int(self.width * self.zoom), int(self.height * self.zoom))
            temp_surface = pygame.transform.scale(surface, scaled_size)
            
            # Calcular offset para centrar
            offset_x = (self.width - scaled_size[0]) // 2
            offset_y = (self.height - scaled_size[1]) // 2
            
            target_surface.blit(temp_surface, (offset_x - self.x * self.zoom, 
                                             offset_y - self.y * self.zoom))
        else:
            target_surface.blit(surface, (-self.x, -self.y))


class CombatEffects:
    """Efectos mejorados de combate"""
    
    @staticmethod
    def create_hit_effect(x, y, damage, critical=False):
        """Crea efectos de impacto mejorados"""
        effects = []
        
        if critical:
            # Efecto de crítico
            for i in range(12):
                angle = (i / 12) * math.pi * 2
                speed = random.randint(200, 400)
                effects.append({
                    'type': 'star',
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'color': (255, 255, 0),
                    'size': random.randint(3, 6),
                    'lifetime': 0.5
                })
        
        # Números de daño
        effects.append({
            'type': 'damage_text',
            'x': x,
            'y': y,
            'text': str(damage),
            'color': (255, 255, 0) if critical else (255, 255, 255),
            'size': 32 if critical else 24,
            'lifetime': 1.0,
            'vy': -100
        })
        
        return effects
    
    @staticmethod
    def create_dash_trail(x, y, angle, color=(100, 200, 255)):
        """Crea estela de dash"""
        trail = []
        for i in range(5):
            offset = i * 10
            trail_x = x - math.cos(angle) * offset
            trail_y = y - math.sin(angle) * offset
            
            trail.append({
                'type': 'trail',
                'x': trail_x,
                'y': trail_y,
                'alpha': 200 - i * 40,
                'color': color,
                'size': 20 - i * 3,
                'lifetime': 0.3
            })
        
        return trail
    
    @staticmethod
    def create_combo_effect(x, y, combo_count):
        """Efecto visual para combos"""
        effects = []
        
        # Texto de combo
        effects.append({
            'type': 'combo_text',
            'x': x,
            'y': y,
            'text': f"COMBO x{combo_count}!",
            'color': (255, 100, 0),
            'size': 36 + combo_count * 2,
            'lifetime': 1.5,
            'pulse': True
        })
        
        # Explosión de partículas
        for i in range(combo_count * 5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            
            effects.append({
                'type': 'particle',
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': (255, random.randint(100, 255), 0),
                'size': random.randint(2, 5),
                'lifetime': random.uniform(0.5, 1.0),
                'gravity': 200
            })
        
        return effects


class GameFeedback:
    """Sistema de retroalimentación del juego"""
    
    def __init__(self):
        self.hit_stop_duration = 0
        self.slow_motion_factor = 1.0
        self.slow_motion_duration = 0
        
    def add_hit_stop(self, duration=0.05):
        """Añade una pausa breve al golpear (hit stop)"""
        self.hit_stop_duration = max(self.hit_stop_duration, duration)
    
    def add_slow_motion(self, factor=0.3, duration=0.5):
        """Añade cámara lenta temporal"""
        self.slow_motion_factor = factor
        self.slow_motion_duration = duration
    
    def update(self, dt):
        """Actualiza los efectos de feedback"""
        # Hit stop
        if self.hit_stop_duration > 0:
            self.hit_stop_duration -= dt
            return 0  # No actualizar nada durante hit stop
        
        # Slow motion
        if self.slow_motion_duration > 0:
            self.slow_motion_duration -= dt
            return dt * self.slow_motion_factor
        else:
            self.slow_motion_factor = 1.0
            
        return dt
    
    def screen_flash(self, screen, color=(255, 255, 255), alpha=128):
        """Flash de pantalla"""
        flash_surface = pygame.Surface((screen.get_width(), screen.get_height()))
        flash_surface.fill(color)
        flash_surface.set_alpha(alpha)
        screen.blit(flash_surface, (0, 0))


class UIEffects:
    """Efectos mejorados de interfaz"""
    
    @staticmethod
    def draw_animated_text(surface, text, x, y, font, base_color, time, 
                          wave=False, pulse=False, shake=False):
        """Dibuja texto con efectos animados"""
        if wave:
            # Efecto de onda
            for i, char in enumerate(text):
                offset_y = math.sin(time * 5 + i * 0.5) * 5
                char_surf = font.render(char, True, base_color)
                char_x = x + i * font.size(char)[0]
                surface.blit(char_surf, (char_x, y + offset_y))
        
        elif pulse:
            # Efecto de pulso
            scale = 1.0 + math.sin(time * 10) * 0.1
            scaled_font = pygame.font.Font(font.get_name(), 
                                         int(font.get_height() * scale))
            text_surf = scaled_font.render(text, True, base_color)
            text_rect = text_surf.get_rect(center=(x, y))
            surface.blit(text_surf, text_rect)
        
        elif shake:
            # Efecto de temblor
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
            text_surf = font.render(text, True, base_color)
            surface.blit(text_surf, (x + shake_x, y + shake_y))
        
        else:
            # Texto normal
            text_surf = font.render(text, True, base_color)
            surface.blit(text_surf, (x, y))
    
    @staticmethod
    def draw_animated_bar(surface, x, y, width, height, current, maximum,
                         color, bg_color, pulse_on_low=True):
        """Dibuja una barra animada"""
        # Calcular porcentaje
        percentage = current / maximum if maximum > 0 else 0
        
        # Efecto de pulso cuando está baja
        if pulse_on_low and percentage < 0.3:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.3
            color = (
                min(255, color[0] + int(255 * pulse)),
                max(0, color[1] - int(100 * pulse)),
                max(0, color[2] - int(100 * pulse))
            )
        
        # Dibujar barra
        VisualEffects.draw_health_bar(surface, x, y, width, height, 
                                     current, maximum, color, bg_color)
        
        # Efecto de brillo en cambios
        if percentage > 0:
            shine_width = int(width * percentage * 0.2)
            shine_x = x + int(width * percentage) - shine_width
            
            if shine_x > x:
                shine_surf = pygame.Surface((shine_width, height), pygame.SRCALPHA)
                shine_surf.fill((255, 255, 255, 100))
                surface.blit(shine_surf, (shine_x, y))


class PowerUpEffects:
    """Efectos visuales para power-ups"""
    
    @staticmethod
    def create_pickup_effect(x, y, powerup_type):
        """Crea efecto al recoger power-up"""
        effects = []
        
        # Colores según tipo
        colors = {
            'health': (0, 255, 0),
            'ammo': (255, 255, 0),
            'speed': (0, 100, 255)
        }
        
        color = colors.get(powerup_type, (255, 255, 255))
        
        # Anillo expansivo
        effects.append({
            'type': 'ring',
            'x': x,
            'y': y,
            'radius': 10,
            'max_radius': 50,
            'color': color,
            'lifetime': 0.5,
            'width': 3
        })
        
        # Partículas
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            speed = random.uniform(100, 200)
            
            effects.append({
                'type': 'particle',
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'size': random.randint(2, 4),
                'lifetime': random.uniform(0.5, 1.0),
                'fade': True
            })
        
        # Texto
        text_map = {
            'health': '+HEALTH',
            'ammo': '+AMMO',
            'speed': '+SPEED'
        }
        
        effects.append({
            'type': 'floating_text',
            'x': x,
            'y': y - 20,
            'text': text_map.get(powerup_type, '+POWER'),
            'color': color,
            'size': 24,
            'lifetime': 1.0,
            'vy': -50
        })
        
        return effects