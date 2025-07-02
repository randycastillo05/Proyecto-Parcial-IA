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
            
            # C