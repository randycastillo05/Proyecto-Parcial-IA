import pygame
import math
import os

class SpriteGenerator:
    """Generador de sprites básico (compatibilidad con proyecto original)"""
    
    @staticmethod
    def create_player_sprite(size=32):
        """Crea sprite básico del jugador"""
        surface = pygame.Surface((size, size))
        surface.fill((0, 255, 0))  # Verde
        return surface
    
    @staticmethod
    def create_enemy_sprite(enemy_type, size=32):
        """Crea sprite básico de enemigo"""
        surface = pygame.Surface((size, size))
        
        if enemy_type == "soldier":
            surface.fill((255, 0, 0))  # Rojo
        elif enemy_type == "elite":
            surface.fill((139, 0, 0))  # Rojo oscuro
        elif enemy_type == "sniper":
            surface.fill((128, 0, 128))  # Púrpura
        elif enemy_type == "kamikaze":
            surface.fill((255, 165, 0))  # Naranja
        elif enemy_type == "officer":
            surface.fill((0, 100, 0))  # Verde oscuro
        else:
            surface.fill((255, 0, 0))  # Rojo por defecto
            
        return surface
    
    @staticmethod
    def create_bullet_sprite(size=6):
        """Crea sprite básico de bala"""
        surface = pygame.Surface((size, size))
        surface.fill((255, 255, 0))  # Amarillo
        return surface
    
    @staticmethod
    def create_powerup_sprite(powerup_type, size=20):
        """Crea sprite básico de power-up"""
        surface = pygame.Surface((size, size))
        
        if powerup_type == "health":
            surface.fill((0, 255, 0))  # Verde
        elif powerup_type == "ammo":
            surface.fill((255, 255, 0))  # Amarillo
        elif powerup_type == "speed":
            surface.fill((0, 0, 255))  # Azul
        else:
            surface.fill((255, 255, 255))  # Blanco
            
        return surface
    
    @staticmethod
    def save_all_sprites(directory="assets/images/generated"):
        """Guarda sprites básicos"""
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
        
        # Otros
        bullet_sprite = SpriteGenerator.create_bullet_sprite()
        pygame.image.save(bullet_sprite, os.path.join(directory, "bullet.png"))
        
        powerup_types = ["health", "ammo", "speed"]
        for powerup_type in powerup_types:
            sprite = SpriteGenerator.create_powerup_sprite(powerup_type)
            pygame.image.save(sprite, os.path.join(directory, f"powerup_{powerup_type}.png"))
        
        print(f"Sprites básicos guardados en {directory}")