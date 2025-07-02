import pygame
import math
import os

class SpriteGenerator:
    """Genera sprites placeholder con estilo para el juego"""
    
    @staticmethod
    def create_player_sprite(size=32):
        """Crea sprite del jugador"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Cuerpo (rectángulo verde militar)
        body_color = (34, 139, 34)
        body_rect = pygame.Rect(size//4, size//4, size//2, size//2)
        pygame.draw.rect(surface, body_color, body_rect)
        pygame.draw.rect(surface, (20, 100, 20), body_rect, 2)
        
        # Casco
        helmet_color = (50, 50, 50)
        helmet_rect = pygame.Rect(size//3, size//6, size//3, size//4)
        pygame.draw.ellipse(surface, helmet_color, helmet_rect)
        
        # Arma (línea negra)
        gun_start = (size//2, size//2)
        gun_end = (size - 2, size//2)
        pygame.draw.line(surface, (0, 0, 0), gun_start, gun_end, 3)
        
        # Indicador de dirección
        pygame.draw.circle(surface, (255, 255, 255), (3*size//4, size//2), 2)
        
        return surface
    
    @staticmethod
    def create_enemy_sprite(enemy_type, size=32):
        """Crea sprites de enemigos según su tipo"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if enemy_type == "soldier":
            # Soldado básico - rojo
            body_color = (200, 0, 0)
            accent_color = (150, 0, 0)
            
            # Cuerpo
            body_rect = pygame.Rect(size//4, size//4, size//2, size//2)
            pygame.draw.rect(surface, body_color, body_rect)
            pygame.draw.rect(surface, accent_color, body_rect, 2)
            
            # Casco
            helmet_rect = pygame.Rect(size//3, size//6, size//3, size//4)
            pygame.draw.ellipse(surface, (100, 0, 0), helmet_rect)
            
            # Arma
            pygame.draw.line(surface, (0, 0, 0), (size//2, size//2), (size-4, size//2), 2)
            
        elif enemy_type == "elite":
            # Elite - rojo oscuro con detalles
            body_color = (139, 0, 0)
            accent_color = (255, 215, 0)  # Detalles dorados
            
            # Cuerpo con armadura
            body_points = [
                (size//3, size//5),
                (2*size//3, size//5),
                (3*size//4, size//2),
                (2*size//3, 3*size//4),
                (size//3, 3*size//4),
                (size//4, size//2)
            ]
            pygame.draw.polygon(surface, body_color, body_points)
            pygame.draw.polygon(surface, accent_color, body_points, 2)
            
            # Visor
            visor_rect = pygame.Rect(size//3, size//4, size//3, size//6)
            pygame.draw.rect(surface, (0, 255, 255), visor_rect)
            
        elif enemy_type == "sniper":
            # Francotirador - púrpura/camuflaje
            body_color = (128, 0, 128)
            camo_color = (100, 0, 100)
            
            # Cuerpo principal primero
            body_rect = pygame.Rect(size//3, size//4, size//3, size//2)
            pygame.draw.rect(surface, body_color, body_rect)
            
            # Patrón de camuflaje
            for y in range(size//4, 3*size//4, 4):
                for x in range(size//3, 2*size//3, 4):
                    if (x + y) % 8 == 0:
                        pygame.draw.rect(surface, camo_color, (x, y, 3, 3))
            
            # Rifle largo
            pygame.draw.line(surface, (0, 0, 0), (size//2, size//2), (size-2, size//2), 3)
            pygame.draw.circle(surface, (50, 50, 50), (size-4, size//2), 3)  # Mira telescópica
            
        elif enemy_type == "kamikaze":
            # Kamikaze - naranja con explosivos
            body_color = (255, 165, 0)
            danger_color = (255, 0, 0)
            
            # Cuerpo
            pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
            
            # Cinturón de explosivos
            for angle in range(0, 360, 45):
                x = size//2 + int(math.cos(math.radians(angle)) * size//4)
                y = size//2 + int(math.sin(math.radians(angle)) * size//4)
                pygame.draw.circle(surface, danger_color, (x, y), 2)
            
            # Cara de loco
            pygame.draw.circle(surface, (255, 255, 255), (size//2-4, size//2-4), 2)
            pygame.draw.circle(surface, (255, 255, 255), (size//2+4, size//2-4), 2)
            pygame.draw.arc(surface, (0, 0, 0), 
                          pygame.Rect(size//3, size//2, size//3, size//4), 
                          0, math.pi, 2)
            
        elif enemy_type == "officer":
            # Oficial - verde oscuro con insignias
            body_color = (0, 100, 0)
            medal_color = (255, 215, 0)
            
            # Cuerpo
            body_rect = pygame.Rect(size//4, size//4, size//2, size//2)
            pygame.draw.rect(surface, body_color, body_rect)
            
            # Gorra de oficial
            hat_points = [
                (size//4, size//4),
                (3*size//4, size//4),
                (3*size//4 + 3, size//5),
                (size//4 - 3, size//5)
            ]
            pygame.draw.polygon(surface, (0, 50, 0), hat_points)
            
            # Medallas
            pygame.draw.circle(surface, medal_color, (size//3, size//2), 2)
            pygame.draw.circle(surface, medal_color, (2*size//3, size//2), 2)
            
            # Bastón de mando
            pygame.draw.line(surface, (139, 69, 19), 
                           (size//2, size//2), (size//2, 3*size//4), 2)
        
        return surface
    
    @staticmethod
    def create_bullet_sprite(size=6):
        """Crea sprite de bala"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Bala amarilla con brillo
        pygame.draw.circle(surface, (255, 255, 0), (size//2, size//2), size//2)
        pygame.draw.circle(surface, (255, 255, 200), (size//2-1, size//2-1), size//4)
        
        return surface
    
    @staticmethod
    def create_powerup_sprite(powerup_type, size=24):
        """Crea sprites de power-ups"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Fondo circular
        if powerup_type == "health":
            bg_color = (0, 255, 0, 128)
            symbol_color = (255, 255, 255)
            
            # Cruz médica
            pygame.draw.circle(surface, bg_color, (size//2, size//2), size//2)
            # Cruz horizontal
            pygame.draw.rect(surface, symbol_color, 
                           (size//4, size//2-2, size//2, 4))
            # Cruz vertical
            pygame.draw.rect(surface, symbol_color, 
                           (size//2-2, size//4, 4, size//2))
            
        elif powerup_type == "ammo":
            bg_color = (255, 255, 0, 128)
            symbol_color = (139, 69, 19)
            
            pygame.draw.circle(surface, bg_color, (size//2, size//2), size//2)
            # Dibujar balas
            for i in range(3):
                x = size//4 + i * size//4
                y = size//2
                pygame.draw.rect(surface, symbol_color, (x, y-4, 3, 8))
                pygame.draw.circle(surface, (255, 215, 0), (x+1, y-4), 2)
                
        elif powerup_type == "speed":
            bg_color = (0, 0, 255, 128)
            symbol_color = (255, 255, 255)
            
            pygame.draw.circle(surface, bg_color, (size//2, size//2), size//2)
            # Rayo de velocidad
            lightning_points = [
                (size//2 + 4, size//4),
                (size//2, size//2),
                (size//2 + 2, size//2),
                (size//2 - 4, 3*size//4),
                (size//2, size//2),
                (size//2 - 2, size//2)
            ]
            pygame.draw.polygon(surface, symbol_color, lightning_points)
        
        # Borde brillante
        pygame.draw.circle(surface, (255, 255, 255, 100), 
                         (size//2, size//2), size//2, 2)
        
        return surface
    
    @staticmethod
    def create_explosion_sprite(frame, max_frames=8, size=64):
        """Crea frames de animación de explosión"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Progreso de la animación
        progress = frame / max_frames
        
        # Radio de la explosión
        max_radius = size // 2
        current_radius = int(max_radius * (1 - progress * 0.5))
        
        # Colores que cambian con el tiempo
        if progress < 0.3:
            # Blanco brillante al inicio
            color = (255, 255, 255)
            alpha = 255
        elif progress < 0.6:
            # Naranja/amarillo
            color = (255, 200 - int(progress * 100), 0)
            alpha = 200
        else:
            # Rojo oscuro y humo
            color = (200 - int(progress * 100), 50, 0)
            alpha = int(255 * (1 - progress))
        
        # Dibujar múltiples círculos para efecto
        for i in range(3):
            r = current_radius - i * 5
            if r > 0:
                c = (
                    max(0, color[0] - i * 30),
                    max(0, color[1] - i * 30),
                    max(0, color[2] - i * 30),
                    max(0, alpha - i * 50)
                )
                
                temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, c[:3] + (c[3],), 
                                 (size//2, size//2), r)
                surface.blit(temp_surface, (0, 0))
        
        return surface
    
    @staticmethod
    def create_muzzle_flash(size=16):
        """Crea destello de disparo"""
        surface = pygame.Surface((size*2, size), pygame.SRCALPHA)
        
        # Destello en forma de estrella
        points = []
        center = (size//2, size//2)
        
        for i in range(8):
            angle = (i / 8) * math.pi * 2
            if i % 2 == 0:
                radius = size
            else:
                radius = size // 2
            
            x = center[0] + int(math.cos(angle) * radius)
            y = center[1] + int(math.sin(angle) * radius)
            points.append((x, y))
        
        # Gradiente de colores
        pygame.draw.polygon(surface, (255, 255, 200), points)
        pygame.draw.polygon(surface, (255, 200, 0), points, 2)
        
        return surface
    
    @staticmethod
    def save_all_sprites(directory="assets/images/generated"):
        """Guarda todos los sprites generados en archivos"""
        # Inicializar pygame si no está inicializado
        if not pygame.get_init():
            pygame.init()
            
        os.makedirs(directory, exist_ok=True)
        
        # Jugador
        player_sprite = SpriteGenerator.create_player_sprite()
        pygame.image.save(player_sprite, os.path.join(directory, "player.png"))
        
        # Enemigos
        enemy_types = ["soldier", "elite", "sniper", "kamikaze", "officer"]
        for enemy_type in enemy_types:
            sprite = SpriteGenerator.create_enemy_sprite(enemy_type)
            pygame.image.save(sprite, os.path.join(directory, f"enemy_{enemy_type}.png"))
        
        # Power-ups
        powerup_types = ["health", "ammo", "speed"]
        for powerup_type in powerup_types:
            sprite = SpriteGenerator.create_powerup_sprite(powerup_type)
            pygame.image.save(sprite, os.path.join(directory, f"powerup_{powerup_type}.png"))
        
        # Otros
        bullet_sprite = SpriteGenerator.create_bullet_sprite()
        pygame.image.save(bullet_sprite, os.path.join(directory, "bullet.png"))
        
        # Animaciones de explosión
        for i in range(8):
            explosion_sprite = SpriteGenerator.create_explosion_sprite(i, 8)
            pygame.image.save(explosion_sprite, 
                            os.path.join(directory, f"explosion_{i}.png"))
        
        print(f"Sprites guardados en {directory}")


class AnimatedSprite(pygame.sprite.Sprite):
    """Sprite animado base"""
    
    def __init__(self, frames, frame_duration=0.1):
        super().__init__()
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.frame_timer = 0
        self.image = frames[0] if frames else pygame.Surface((32, 32))
        self.rect = self.image.get_rect()
        
    def update(self, dt):
        """Actualiza la animación"""
        if len(self.frames) > 1:
            self.frame_timer += dt
            
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]