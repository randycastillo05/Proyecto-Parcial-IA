import pygame
import math
import random

class VisualEffects:
    """Efectos visuales mejorados para hacer el juego más atractivo"""
    
    @staticmethod
    def create_gradient_background(width, height, color1=(20, 30, 40), color2=(40, 60, 80)):
        """Crea un fondo con gradiente"""
        surface = pygame.Surface((width, height))
        
        for y in range(height):
            # Interpolar entre los dos colores
            ratio = y / height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
            
        return surface
    
    @staticmethod
    def create_tile_texture(size=32, tile_type="grass"):
        """Crea texturas para los tiles del suelo"""
        surface = pygame.Surface((size, size))
        
        if tile_type == "grass":
            # Base verde
            base_color = (34, 139, 34)
            surface.fill(base_color)
            
            # Añadir variación
            for _ in range(20):
                x = random.randint(0, size)
                y = random.randint(0, size)
                shade = random.randint(-20, 20)
                color = (
                    max(0, min(255, base_color[0] + shade)),
                    max(0, min(255, base_color[1] + shade)),
                    max(0, min(255, base_color[2] + shade))
                )
                pygame.draw.circle(surface, color, (x, y), 1)
                
        elif tile_type == "dirt":
            # Base marrón
            base_color = (139, 90, 43)
            surface.fill(base_color)
            
            # Textura de tierra
            for _ in range(15):
                x = random.randint(0, size)
                y = random.randint(0, size)
                w = random.randint(2, 5)
                h = random.randint(2, 5)
                shade = random.randint(-30, 30)
                color = (
                    max(0, min(255, base_color[0] + shade)),
                    max(0, min(255, base_color[1] + shade)),
                    max(0, min(255, base_color[2] + shade))
                )
                pygame.draw.ellipse(surface, color, (x, y, w, h))
                
        elif tile_type == "stone":
            # Base gris
            base_color = (105, 105, 105)
            surface.fill(base_color)
            
            # Grietas
            for _ in range(5):
                start_x = random.randint(0, size)
                start_y = random.randint(0, size)
                end_x = start_x + random.randint(-10, 10)
                end_y = start_y + random.randint(-10, 10)
                pygame.draw.line(surface, (70, 70, 70), 
                               (start_x, start_y), (end_x, end_y), 1)
        
        # Añadir bordes sutiles
        pygame.draw.rect(surface, (0, 0, 0, 30), (0, 0, size, size), 1)
        
        return surface
    
    @staticmethod
    def create_obstacle_sprite(obstacle_type="wall", size=32):
        """Crea sprites mejorados para obstáculos"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if obstacle_type == "wall":
            # Muro de ladrillos
            brick_color = (139, 69, 19)
            mortar_color = (160, 160, 160)
            
            # Fondo
            surface.fill(mortar_color)
            
            # Ladrillos
            brick_height = size // 4
            brick_width = size // 2
            
            for row in range(4):
                for col in range(2):
                    x = col * brick_width + (brick_width//2 if row % 2 else 0)
                    y = row * brick_height
                    
                    if x + brick_width <= size:
                        # Ladrillo principal
                        brick_rect = pygame.Rect(x + 1, y + 1, brick_width - 2, brick_height - 2)
                        pygame.draw.rect(surface, brick_color, brick_rect)
                        
                        # Sombra del ladrillo
                        shadow_color = (100, 50, 10)
                        pygame.draw.line(surface, shadow_color, 
                                       (x + 1, y + brick_height - 1),
                                       (x + brick_width - 1, y + brick_height - 1))
                        pygame.draw.line(surface, shadow_color,
                                       (x + brick_width - 1, y + 1),
                                       (x + brick_width - 1, y + brick_height - 1))
                        
        elif obstacle_type == "barrel":
            # Barril
            barrel_color = (101, 67, 33)
            metal_color = (192, 192, 192)
            
            # Cuerpo del barril
            pygame.draw.ellipse(surface, barrel_color, 
                              (size//6, size//8, 2*size//3, 3*size//4))
            
            # Bandas metálicas
            band_positions = [size//4, size//2, 3*size//4]
            for y in band_positions:
                pygame.draw.rect(surface, metal_color,
                               (size//6, y-2, 2*size//3, 4))
                
            # Sombra
            pygame.draw.ellipse(surface, (0, 0, 0, 100),
                              (size//6, 3*size//4, 2*size//3, size//8))
                              
        elif obstacle_type == "crate":
            # Caja de madera
            wood_color = (139, 90, 43)
            dark_wood = (101, 67, 33)
            
            # Base
            pygame.draw.rect(surface, wood_color, (2, 2, size-4, size-4))
            
            # Tablones
            for i in range(0, size, size//4):
                pygame.draw.line(surface, dark_wood, (2, i), (size-2, i), 1)
                pygame.draw.line(surface, dark_wood, (i, 2), (i, size-2), 1)
            
            # Clavos
            nail_positions = [(size//4, size//4), (3*size//4, size//4),
                            (size//4, 3*size//4), (3*size//4, 3*size//4)]
            for x, y in nail_positions:
                pygame.draw.circle(surface, (80, 80, 80), (x, y), 1)
                
        elif obstacle_type == "tree":
            # Árbol (vista superior)
            # Tronco
            trunk_color = (101, 67, 33)
            pygame.draw.circle(surface, trunk_color, (size//2, size//2), size//6)
            
            # Hojas
            leaf_color = (34, 139, 34)
            for angle in range(0, 360, 30):
                x = size//2 + int(math.cos(math.radians(angle)) * size//3)
                y = size//2 + int(math.sin(math.radians(angle)) * size//3)
                pygame.draw.circle(surface, leaf_color, (x, y), size//4)
            
            # Centro más oscuro
            pygame.draw.circle(surface, (20, 100, 20), (size//2, size//2), size//8)
        
        return surface
    
    @staticmethod
    def create_lighting_overlay(width, height, light_sources):
        """Crea una capa de iluminación dinámica"""
        overlay = pygame.Surface((width, height))
        overlay.fill((20, 20, 30))  # Oscuridad base
        
        for source in light_sources:
            x, y, radius, intensity = source
            
            # Crear gradiente radial
            for r in range(radius, 0, -2):
                alpha = int(255 * (r / radius) * intensity)
                color = (alpha, alpha, int(alpha * 0.8))
                pygame.draw.circle(overlay, color, (int(x), int(y)), r)
        
        overlay.set_alpha(200)
        return overlay
    
    @staticmethod
    def draw_health_bar(surface, x, y, width, height, current, maximum, 
                       color=(0, 255, 0), bg_color=(100, 0, 0)):
        """Dibuja una barra de vida estilizada"""
        # Fondo
        bg_rect = pygame.Rect(x-2, y-2, width+4, height+4)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, border_radius=2)
        
        # Barra de fondo
        pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=1)
        
        # Barra de vida actual
        current_width = int(width * (current / maximum))
        if current_width > 0:
            # Gradiente de color según vida
            if current / maximum > 0.6:
                bar_color = color
            elif current / maximum > 0.3:
                bar_color = (255, 255, 0)  # Amarillo
            else:
                bar_color = (255, 0, 0)  # Rojo
                
            pygame.draw.rect(surface, bar_color, 
                           (x, y, current_width, height), border_radius=1)
            
            # Brillo
            pygame.draw.rect(surface, (255, 255, 255, 100),
                           (x, y, current_width, height//3), border_radius=1)
        
        # Borde
        pygame.draw.rect(surface, (200, 200, 200), (x, y, width, height), 1, border_radius=1)
    
    @staticmethod
    def create_minimap_background(size=150):
        """Crea un fondo estilizado para el minimapa"""
        surface = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        
        # Marco exterior
        pygame.draw.rect(surface, (100, 100, 100, 200), (0, 0, size + 20, size + 20), border_radius=5)
        pygame.draw.rect(surface, (200, 200, 200, 255), (0, 0, size + 20, size + 20), 2, border_radius=5)
        
        # Fondo del radar con líneas de cuadrícula
        radar_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        radar_surface.fill((0, 20, 0, 180))
        
        # Líneas de cuadrícula
        grid_color = (0, 100, 0, 100)
        for i in range(0, size, size // 5):
            pygame.draw.line(radar_surface, grid_color, (i, 0), (i, size), 1)
            pygame.draw.line(radar_surface, grid_color, (0, i), (size, i), 1)
        
        # Círculos concéntricos
        center = size // 2
        for radius in range(25, size // 2, 25):
            pygame.draw.circle(radar_surface, grid_color, (center, center), radius, 1)
        
        surface.blit(radar_surface, (10, 10))
        
        return surface
    
    @staticmethod
    def create_damage_vignette(width, height, intensity=0.5):
        """Crea un efecto de viñeta roja para daño"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Crear gradiente radial desde los bordes
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for radius in range(int(max_radius), int(max_radius * 0.5), -5):
            alpha = int(255 * intensity * (1 - radius / max_radius))
            color = (255, 0, 0, alpha)
            
            # Dibujar rectángulo con bordes redondeados
            rect = pygame.Rect(center_x - radius, center_y - radius * 0.75,
                             radius * 2, radius * 1.5)
            
            if rect.width > 0 and rect.height > 0:
                pygame.draw.ellipse(surface, color, rect)
        
        return surface
    
    @staticmethod
    def draw_score_popup(surface, x, y, score, timer):
        """Dibuja un popup de puntuación que flota hacia arriba"""
        if timer <= 0:
            return
            
        # Calcular posición y transparencia
        float_y = y - (1 - timer) * 30
        alpha = int(255 * timer)
        
        # Crear texto
        font = pygame.font.Font(None, 24)
        text = font.render(f"+{score}", True, (255, 255, 0))
        
        # Añadir sombra
        shadow = font.render(f"+{score}", True, (0, 0, 0))
        
        # Dibujar
        surface.blit(shadow, (x + 2, float_y + 2))
        surface.blit(text, (x, float_y))


class WeatherEffects:
    """Sistema de efectos climáticos"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rain_particles = []
        self.fog_surface = None
        self.lightning_timer = 0
        self.lightning_flash = 0
        
        # Inicializar partículas de lluvia
        for _ in range(100):
            self.rain_particles.append({
                'x': random.randint(0, width),
                'y': random.randint(-height, 0),
                'speed': random.randint(300, 500),
                'length': random.randint(10, 20)
            })
    
    def update_rain(self, dt):
        """Actualiza las partículas de lluvia"""
        for particle in self.rain_particles:
            particle['y'] += particle['speed'] * dt
            
            # Reiniciar si sale de la pantalla
            if particle['y'] > self.height:
                particle['y'] = random.randint(-100, -10)
                particle['x'] = random.randint(0, self.width)
    
    def draw_rain(self, surface):
        """Dibuja la lluvia"""
        for particle in self.rain_particles:
            pygame.draw.line(surface, (150, 150, 255, 100),
                           (particle['x'], particle['y']),
                           (particle['x'] - 2, particle['y'] + particle['length']), 1)
    
    def create_fog(self, density=0.3):
        """Crea efecto de niebla"""
        if not self.fog_surface:
            self.fog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
        self.fog_surface.fill((200, 200, 200, int(255 * density)))
        
        # Añadir variación
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(50, 150)
            pygame.draw.circle(self.fog_surface, (220, 220, 220, int(128 * density)),
                             (x, y), radius)
        
        return self.fog_surface