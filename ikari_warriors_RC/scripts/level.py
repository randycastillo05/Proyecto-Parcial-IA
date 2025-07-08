"""
Randy Castillo
Módulo de Niveles
Gestiona la creación de niveles y obstáculos
"""

import pygame
import os

# Colores
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)

def load_sprite(path, size=None, color_fallback=None):
    """Intenta cargar un sprite, si no existe usa un color"""
    if os.path.exists(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            return image
        except:
            pass
    
    # Fallback: crear superficie con color
    if size:
        surface = pygame.Surface(size)
        surface.fill(color_fallback or GRAY)
        return surface
    return None

class Wall(pygame.sprite.Sprite):
    """Clase para las paredes/obstáculos"""
    def __init__(self, x, y, width, height):
        super().__init__()
        
        # Intentar cargar sprite de pared
        self.image = load_sprite("assets/images/wall.png", (width, height), GRAY)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Floor(pygame.sprite.Sprite):
    """Clase para el suelo"""
    def __init__(self, x, y, width, height):
        super().__init__()
        
        # Intentar cargar sprite de suelo
        self.image = load_sprite("assets/images/floor.png", (width, height), BROWN)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Level:
    """Clase que gestiona los niveles"""
    def __init__(self, level_number):
        self.level_number = level_number
        
        # Diseños de niveles (1 = pared, 0 = vacío)
        self.level_1 = [
            "11111111111111111111"
        ]
        
    def create_walls(self, wall_group, all_sprites):
        """Crea las paredes del nivel"""
        level_data = self.level_1  # Por ahora solo nivel 1
        
        tile_size = 40
        
        # Primero dibujar todo el suelo
        for row_index in range(len(level_data)):
            for col_index in range(len(level_data[0])):
                x = col_index * tile_size
                y = row_index * tile_size
                floor = Floor(x, y, tile_size, tile_size)
                all_sprites.add(floor)
        
        # Luego las paredes encima
        for row_index, row in enumerate(level_data):
            for col_index, cell in enumerate(row):
                if cell == '1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    wall = Wall(x, y, tile_size, tile_size)
                    wall_group.add(wall)
                    all_sprites.add(wall),
            "10000000000000000001",
            "10110000110000110001",
            "10000000000000000001",
            "10000000000000000001",
            "11111111111111111111",
            "10001111111111100001",
            "10000000000000000001",
            "10110000110000110001",
            "10000000000000000001",
            "10001111111111100001",
            "10000000000000000001",
            "10110000110000110001",
            "10000000000000000001"