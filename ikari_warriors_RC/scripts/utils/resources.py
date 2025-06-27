import pygame
import os

class ResourceManager:
    """Clase para gestionar la carga de recursos"""
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.music = {}
        self.fonts = {}
        
        # Rutas base
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.assets_path = os.path.join(self.base_path, "assets")
        self.images_path = os.path.join(self.assets_path, "images")
        self.sounds_path = os.path.join(self.assets_path, "sounds")
        
        # Cargar recursos básicos
        self.load_basic_resources()
        
    def load_basic_resources(self):
        """Carga recursos básicos del juego"""
        # Por ahora no cargamos nada, pero aquí irían las imágenes
        pass
        
    def load_image(self, name, path):
        """Carga una imagen"""
        try:
            full_path = os.path.join(self.images_path, path)
            self.images[name] = pygame.image.load(full_path).convert_alpha()
            print(f"Imagen cargada: {name}")
        except:
            print(f"Error al cargar imagen: {path}")
            # Crear una superficie temporal
            self.images[name] = pygame.Surface((32, 32))
            self.images[name].fill((255, 0, 255))  # Magenta para indicar error
            
    def get_image(self, name):
        """Obtiene una imagen cargada"""
        return self.images.get(name, None)
        
    def load_sound(self, name, path):
        """Carga un sonido"""
        try:
            full_path = os.path.join(self.sounds_path, path)
            self.sounds[name] = pygame.mixer.Sound(full_path)
            print(f"Sonido cargado: {name}")
        except:
            print(f"Error al cargar sonido: {path}")