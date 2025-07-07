import pygame
import math
import random
import os

class EnhancedSprites:
    """Generador de sprites mejorados con efectos visuales"""
    
    @staticmethod
    def create_detailed_bullet(size=16):
        """Bala mejorada con mejor visibilidad"""
        surface = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
        center_x = size * 1.5
        center_y = size
        
        # Glow exterior grande
        for i in range(10, 0, -1):
            alpha = int(25 * (i / 10))
            glow_size = size + i * 2
            glow_color = (255, 255, 100, alpha)
            
            glow_surface = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, 
                            (int(center_x), int(center_y)), glow_size)
            surface.blit(glow_surface, (0, 0))
        
        # Núcleo brillante blanco
        core_size = size // 2
        pygame.draw.circle(surface, (255, 255, 255), 
                        (int(center_x), int(center_y)), core_size)
        
        # Anillo amarillo brillante
        pygame.draw.circle(surface, (255, 255, 0), 
                        (int(center_x), int(center_y)), core_size + 2, 2)
        
        # Punto central super brillante
        pygame.draw.circle(surface, (255, 255, 255), 
                        (int(center_x), int(center_y)), 2)
        
        # Trail mejorado más visible
        trail_length = 8
        for i in range(trail_length):
            trail_alpha = int(200 - (i * 25))
            trail_size = core_size - (i * 0.5)
            if trail_size > 0 and trail_alpha > 0:
                trail_x = center_x - (i + 1) * 4
                trail_color = (255, 200 - i * 20, 0, trail_alpha)
                
                trail_surface = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color[:3], 
                                (int(trail_x), int(center_y)), int(trail_size))
                trail_surface.set_alpha(trail_alpha)
                surface.blit(trail_surface, (0, 0))
        
        return surface
    
    @staticmethod
    def create_detailed_player(size=48):
        """Jugador mejorado con contorno brillante"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo principal (verde militar)
        body_color = (60, 180, 60)
        pygame.draw.circle(surface, body_color, (center, center), center - 4)
        
        # Chaleco (verde más oscuro)
        vest_color = (50, 150, 50)
        vest_rect = pygame.Rect(center - 12, center - 8, 24, 16)
        pygame.draw.rect(surface, vest_color, vest_rect)
        
        # Casco
        helmet_color = (70, 140, 70)
        pygame.draw.circle(surface, helmet_color, (center, center - 8), 10)
        
        # Botas
        boot_color = (40, 40, 40)
        pygame.draw.rect(surface, boot_color, (center - 8, center + 10, 6, 8))
        pygame.draw.rect(surface, boot_color, (center + 2, center + 10, 6, 8))
        
        # Manos
        hand_color = (220, 180, 130)
        pygame.draw.circle(surface, hand_color, (center - 12, center), 3)
        pygame.draw.circle(surface, hand_color, (center + 12, center), 3)
        
        # Detalles del equipo
        pygame.draw.rect(surface, (80, 80, 80), (center - 2, center - 4, 4, 8))  # Arma
        pygame.draw.circle(surface, (200, 200, 200), (center - 8, center - 8), 2)  # Insignia
        
        # Añadir contorno brillante
        return EnhancedSprites.add_bright_outline(surface, size)
    
    @staticmethod
    def add_bright_outline(surface, size):
        """Añade contorno brillante a cualquier sprite"""
        outline_size = 4  # Tamaño del contorno
        outline_color = (255, 255, 255)  # Blanco para el contorno
        
        # Crear superficie expandida para el outline
        expanded_size = size + outline_size * 2
        outline_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA)
        
        # Posiciones para crear el efecto de outline
        outline_positions = [
            (-outline_size, -outline_size), (0, -outline_size), (outline_size, -outline_size),
            (-outline_size, 0), (outline_size, 0),
            (-outline_size, outline_size), (0, outline_size), (outline_size, outline_size)
        ]
        
        # Dibujar el sprite en múltiples posiciones para crear outline
        for dx, dy in outline_positions:
            outline_surface.blit(surface, (outline_size + dx, outline_size + dy))

        try:
            # Crear máscara y aplicar color
            mask = pygame.mask.from_surface(outline_surface)
            colored_outline = mask.to_surface(setcolor=outline_color)
            colored_outline.set_alpha(100)  # Semi-transparente
        except:
            # Fallback si mask no funciona
            colored_outline = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA)
            colored_outline.fill((*outline_color, 100))

        # Nueva superficie final con outline
        final_surface = pygame.Surface((expanded_size, expanded_size), pygame.SRCALPHA)
        final_surface.blit(colored_outline, (0, 0))
        final_surface.blit(surface, (outline_size, outline_size))

        return final_surface
    
    @staticmethod
    def create_detailed_soldier(size=32):
        """Soldado enemigo detallado"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo (rojo militar)
        body_color = (180, 60, 60)
        pygame.draw.circle(surface, body_color, (center, center), center - 2)
        
        # Uniforme
        uniform_color = (150, 50, 50)
        pygame.draw.rect(surface, uniform_color, (center - 8, center - 6, 16, 12))
        
        # Casco
        helmet_color = (100, 40, 40)
        pygame.draw.circle(surface, helmet_color, (center, center - 6), 8)
        
        # Arma
        weapon_color = (80, 80, 80)
        pygame.draw.rect(surface, weapon_color, (center - 1, center - 2, 2, 6))
        
        return surface
    
    @staticmethod
    def create_detailed_elite(size=32):
        """Soldado élite con mejor equipamiento"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo (rojo oscuro)
        body_color = (139, 0, 0)
        pygame.draw.circle(surface, body_color, (center, center), center - 2)
        
        # Armadura
        armor_color = (100, 0, 0)
        pygame.draw.rect(surface, armor_color, (center - 10, center - 8, 20, 16))
        
        # Casco avanzado
        helmet_color = (80, 0, 0)
        pygame.draw.circle(surface, helmet_color, (center, center - 6), 9)
        
        # Visor
        visor_color = (0, 255, 0)
        pygame.draw.rect(surface, visor_color, (center - 6, center - 8, 12, 3))
        
        # Arma mejorada
        weapon_color = (120, 120, 120)
        pygame.draw.rect(surface, weapon_color, (center - 2, center - 3, 4, 8))
        
        return surface
    
    @staticmethod
    def create_detailed_sniper(size=32):
        """Francotirador con rifle largo"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo (púrpura)
        body_color = (128, 0, 128)
        pygame.draw.circle(surface, body_color, (center, center), center - 2)
        
        # Traje de camuflaje
        camo_color = (100, 0, 100)
        pygame.draw.rect(surface, camo_color, (center - 8, center - 6, 16, 12))
        
        # Casco de francotirador
        helmet_color = (80, 0, 80)
        pygame.draw.circle(surface, helmet_color, (center, center - 6), 8)
        
        # Mira telescópica
        scope_color = (200, 200, 200)
        pygame.draw.circle(surface, scope_color, (center - 8, center - 6), 3)
        
        # Rifle largo
        rifle_color = (60, 60, 60)
        pygame.draw.rect(surface, rifle_color, (center - 12, center, 16, 2))
        
        return surface
    
    @staticmethod
    def create_detailed_kamikaze(size=32):
        """Kamikaze con explosivos"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo (naranja)
        body_color = (255, 165, 0)
        pygame.draw.circle(surface, body_color, (center, center), center - 2)
        
        # Chaleco explosivo
        vest_color = (200, 100, 0)
        pygame.draw.rect(surface, vest_color, (center - 10, center - 8, 20, 16))
        
        # Dinamita visible
        dynamite_color = (255, 0, 0)
        for i in range(3):
            x = center - 6 + i * 4
            pygame.draw.rect(surface, dynamite_color, (x, center - 4, 2, 8))
        
        # Cables
        wire_color = (0, 0, 0)
        pygame.draw.line(surface, wire_color, (center - 6, center), (center + 6, center), 1)
        
        # Detonador
        detonator_color = (255, 255, 0)
        pygame.draw.circle(surface, detonator_color, (center + 8, center - 8), 3)
        
        return surface
    
    @staticmethod
    def create_detailed_officer(size=32):
        """Oficial con insignias"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Cuerpo (verde oscuro)
        body_color = (0, 100, 0)
        pygame.draw.circle(surface, body_color, (center, center), center - 2)
        
        # Uniforme de oficial
        uniform_color = (0, 80, 0)
        pygame.draw.rect(surface, uniform_color, (center - 10, center - 8, 20, 16))
        
        # Gorra de oficial
        cap_color = (0, 60, 0)
        pygame.draw.rect(surface, cap_color, (center - 8, center - 10, 16, 6))
        
        # Insignias doradas
        insignia_color = (255, 215, 0)
        pygame.draw.circle(surface, insignia_color, (center - 6, center - 4), 2)
        pygame.draw.circle(surface, insignia_color, (center + 6, center - 4), 2)
        
        # Bastón de mando
        baton_color = (139, 69, 19)
        pygame.draw.rect(surface, baton_color, (center + 8, center - 8, 2, 12))
        
        return surface
    
    @staticmethod
    def create_detailed_powerup(powerup_type, size=32):
        """Power-ups detallados según tipo"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if powerup_type == "health":
            # Cruz médica
            cross_color = (255, 255, 255)
            pygame.draw.rect(surface, cross_color, (center - 2, center - 8, 4, 16))
            pygame.draw.rect(surface, cross_color, (center - 8, center - 2, 16, 4))
            
            # Fondo rojo
            bg_color = (255, 0, 0)
            pygame.draw.circle(surface, bg_color, (center, center), center - 4)
            
            # Borde blanco
            pygame.draw.circle(surface, cross_color, (center, center), center - 4, 2)
            
        elif powerup_type == "ammo":
            # Bala grande
            bullet_color = (255, 215, 0)
            pygame.draw.rect(surface, bullet_color, (center - 4, center - 8, 8, 16))
            
            # Punta
            tip_color = (255, 255, 0)
            pygame.draw.polygon(surface, tip_color, [
                (center, center - 12),
                (center - 4, center - 8),
                (center + 4, center - 8)
            ])
            
            # Base
            base_color = (200, 150, 0)
            pygame.draw.rect(surface, base_color, (center - 4, center + 4, 8, 4))
            
        elif powerup_type == "speed":
            # Rayo/relámpago
            lightning_color = (0, 191, 255)
            points = [
                (center - 4, center - 10),
                (center + 2, center - 2),
                (center - 2, center),
                (center + 4, center + 10),
                (center - 2, center + 2),
                (center + 2, center)
            ]
            pygame.draw.polygon(surface, lightning_color, points)
            
            # Efectos de brillo
            glow_color = (173, 216, 230)
            for i in range(1, 4):
                pygame.draw.polygon(surface, glow_color, points, i)
        
        # Añadir efecto de brillo general
        for i in range(3):
            alpha = 100 - i * 30
            glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, alpha), (center, center), center - 2 + i * 2)
            surface.blit(glow_surface, (0, 0))
        
        return surface
    
    @staticmethod
    def create_explosion_animation(frames=8, size=64):
        """Crea frames de animación de explosión"""
        explosion_frames = []
        center = size // 2
        
        for frame in range(frames):
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            progress = frame / (frames - 1)
            
            # Colores que cambian con el tiempo
            if progress < 0.3:
                # Inicio - blanco brillante
                colors = [(255, 255, 255), (255, 255, 200), (255, 200, 100)]
            elif progress < 0.6:
                # Medio - amarillo/naranja
                colors = [(255, 200, 100), (255, 150, 0), (255, 100, 0)]
            else:
                # Final - rojo/humo
                colors = [(255, 100, 0), (200, 50, 0), (100, 100, 100)]
            
            # Dibujar círculos concéntricos
            for i, color in enumerate(colors):
                radius = int((center - i * 5) * (0.5 + progress * 0.5))
                if radius > 0:
                    alpha = int(255 * (1 - progress))
                    explosion_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.circle(explosion_surface, (*color, alpha), (center, center), radius)
                    surface.blit(explosion_surface, (0, 0))
            
            # Añadir partículas aleatorias
            for _ in range(int(20 * (1 - progress))):
                x = center + random.randint(-center, center)
                y = center + random.randint(-center, center)
                particle_size = random.randint(1, 3)
                particle_color = random.choice(colors)
                pygame.draw.circle(surface, particle_color, (x, y), particle_size)
            
            explosion_frames.append(surface)
        
        return explosion_frames
    
    @staticmethod
    def save_all_enhanced_sprites(directory="assets/images/enhanced"):
        """Guarda todos los sprites mejorados"""
        if not pygame.get_init():
            pygame.init()
            
        os.makedirs(directory, exist_ok=True)
        
        try:
            # Jugador
            player_sprite = EnhancedSprites.create_detailed_player()
            pygame.image.save(player_sprite, os.path.join(directory, "player.png"))
            
            # Enemigos
            enemy_creators = {
                "soldier": EnhancedSprites.create_detailed_soldier,
                "elite": EnhancedSprites.create_detailed_elite,
                "sniper": EnhancedSprites.create_detailed_sniper,
                "kamikaze": EnhancedSprites.create_detailed_kamikaze,
                "officer": EnhancedSprites.create_detailed_officer
            }
            
            for enemy_type, creator in enemy_creators.items():
                sprite = creator()
                pygame.image.save(sprite, os.path.join(directory, f"enemy_{enemy_type}.png"))
            
            # Bala
            bullet_sprite = EnhancedSprites.create_detailed_bullet()
            pygame.image.save(bullet_sprite, os.path.join(directory, "bullet.png"))
            
            # Power-ups
            powerup_types = ["health", "ammo", "speed"]
            for powerup_type in powerup_types:
                sprite = EnhancedSprites.create_detailed_powerup(powerup_type)
                pygame.image.save(sprite, os.path.join(directory, f"powerup_{powerup_type}.png"))
            
            # Explosiones
            explosion_frames = EnhancedSprites.create_explosion_animation()
            for i, frame in enumerate(explosion_frames):
                pygame.image.save(frame, os.path.join(directory, f"explosion_{i}.png"))
            
            print(f"✅ Sprites mejorados guardados en {directory}")
            
        except Exception as e:
            print(f"❌ Error guardando sprites: {e}")

def generate_enhanced_sprites():
    """Genera todos los sprites mejorados"""
    
    # IMPORTANTE: Inicializar Pygame y el display si no se ha hecho
    if not pygame.get_init():
        pygame.init()
    
    # Crear una superficie de display dummy o real para asegurar el contexto gráfico
    # No es necesario que se vea, solo que exista para las operaciones de dibujo.
    # Puedes usar un tamaño pequeño si no quieres una ventana visible.
    try:
        # Intenta establecer un modo de video oculto si es posible
        # pygame.FULLSCREEN | pygame.HIDDEN podría funcionar en algunos sistemas,
        # o simplemente un tamaño muy pequeño y sin flip.
        screen = pygame.display.set_mode((1, 1), pygame.HIDDEN) 
    except pygame.error:
        # Si HIDDEN no funciona, crea una ventana normal pero que se cierre rápido
        screen = pygame.display.set_mode((100, 100)) # Un tamaño pequeño
        pygame.display.iconify() # Minimizar la ventana
        print("Advertencia: Se creó una pequeña ventana Pygame temporal para la generación de sprites.")

    EnhancedSprites.save_all_enhanced_sprites()
    
    # Quitar el display de Pygame después de generar los sprites si lo creaste solo para esto
    pygame.display.quit()
    pygame.quit() # Opcional, pero limpia completamente Pygame

if __name__ == "__main__":
    generate_enhanced_sprites()