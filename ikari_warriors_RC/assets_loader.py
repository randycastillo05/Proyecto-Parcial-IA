#!/usr/bin/env python3
"""
Sistema de sprites mejorados para Ikari Warriors
Integración segura con el proyecto existente
"""

import pygame
import math
import os
import random
from scripts.utils.constants import *

class EnhancedSprites:
    """Sistema de sprites mejorados que se integra con el proyecto existente"""
    
    @staticmethod
    def setup_enhanced_sprites():
        """Configura todos los sprites mejorados y los guarda"""
        print("🎨 Configurando sprites mejorados...")
        
        # Inicializar pygame si no está inicializado
        if not pygame.get_init():
            pygame.init()
        
        # Crear directorio de sprites mejorados
        sprites_dir = os.path.join("assets", "images", "enhanced")
        os.makedirs(sprites_dir, exist_ok=True)
        
        # Generar todos los sprites
        sprites_generated = 0
        
        # Jugador
        player_sprite = EnhancedSprites.create_detailed_player()
        pygame.image.save(player_sprite, os.path.join(sprites_dir, "player.png"))
        sprites_generated += 1
        print("✓ Jugador mejorado generado")
        
        # Enemigos
        enemy_types = {
            EnemyType.SOLDIER: EnhancedSprites.create_detailed_soldier(),
            EnemyType.ELITE: EnhancedSprites.create_detailed_elite(),
            EnemyType.SNIPER: EnhancedSprites.create_detailed_sniper(),
            EnemyType.KAMIKAZE: EnhancedSprites.create_detailed_kamikaze(),
            EnemyType.OFFICER: EnhancedSprites.create_detailed_officer()
        }
        
        for enemy_type, sprite in enemy_types.items():
            filename = f"enemy_{enemy_type}.png"
            pygame.image.save(sprite, os.path.join(sprites_dir, filename))
            sprites_generated += 1
            print(f"✓ Enemigo {enemy_type} mejorado generado")
        
        # Proyectiles
        bullet_sprite = EnhancedSprites.create_detailed_bullet()
        pygame.image.save(bullet_sprite, os.path.join(sprites_dir, "bullet.png"))
        sprites_generated += 1
        print("✓ Bala mejorada generada")
        
        # Power-ups
        powerup_types = ["health", "ammo", "speed"]
        for powerup_type in powerup_types:
            sprite = EnhancedSprites.create_detailed_powerup(powerup_type)
            filename = f"powerup_{powerup_type}.png"
            pygame.image.save(sprite, os.path.join(sprites_dir, filename))
            sprites_generated += 1
            print(f"✓ Power-up {powerup_type} mejorado generado")
        
        # Efectos
        explosion_frames = EnhancedSprites.create_explosion_animation()
        for i, frame in enumerate(explosion_frames):
            filename = f"explosion_{i}.png"
            pygame.image.save(frame, os.path.join(sprites_dir, filename))
            sprites_generated += 1
        print(f"✓ {len(explosion_frames)} frames de explosión generados")
        
        print(f"🎉 ¡{sprites_generated} sprites mejorados generados en {sprites_dir}!")
        return sprites_dir
    
    @staticmethod
    def create_detailed_player(size=48):
        """Jugador con uniforme militar detallado"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra realista
        shadow_color = (0, 0, 0, 80)
        pygame.draw.ellipse(surface, shadow_color, 
                          (center_x - 12, center_y + 18, 24, 8))
        
        # Cuerpo principal (uniforme verde militar)
        body_color = (45, 120, 45)
        body_rect = pygame.Rect(center_x - 10, center_y - 12, 20, 24)
        pygame.draw.ellipse(surface, body_color, body_rect)
        
        # Chaleco antibalas con detalles
        vest_color = (35, 90, 35)
        vest_rect = pygame.Rect(center_x - 8, center_y - 10, 16, 20)
        pygame.draw.rect(surface, vest_color, vest_rect, border_radius=3)
        
        # Bolsillos del chaleco
        pocket_color = (25, 70, 25)
        pygame.draw.rect(surface, pocket_color, (center_x - 6, center_y - 8, 5, 4), border_radius=1)
        pygame.draw.rect(surface, pocket_color, (center_x + 1, center_y - 8, 5, 4), border_radius=1)
        pygame.draw.rect(surface, pocket_color, (center_x - 6, center_y - 2, 5, 4), border_radius=1)
        pygame.draw.rect(surface, pocket_color, (center_x + 1, center_y - 2, 5, 4), border_radius=1)
        
        # Casco militar detallado
        helmet_color = (40, 60, 40)
        helmet_rect = pygame.Rect(center_x - 9, center_y - 18, 18, 12)
        pygame.draw.ellipse(surface, helmet_color, helmet_rect)
        
        # Banda del casco
        pygame.draw.rect(surface, (30, 45, 30), (center_x - 8, center_y - 12, 16, 3))
        
        # Gafas tácticas
        pygame.draw.circle(surface, (20, 20, 20), (center_x - 3, center_y - 10), 3, 1)
        pygame.draw.circle(surface, (20, 20, 20), (center_x + 3, center_y - 10), 3, 1)
        pygame.draw.line(surface, (20, 20, 20), (center_x - 3, center_y - 10), (center_x + 3, center_y - 10), 1)
        
        # Brazos musculosos
        arm_color = body_color
        # Brazo izquierdo
        pygame.draw.ellipse(surface, arm_color, (center_x - 14, center_y - 6, 8, 16))
        # Brazo derecho (sosteniendo arma)
        pygame.draw.ellipse(surface, arm_color, (center_x + 6, center_y - 6, 8, 16))
        
        # Piernas con músculos
        leg_color = (35, 85, 35)
        # Pierna izquierda
        pygame.draw.ellipse(surface, leg_color, (center_x - 7, center_y + 8, 6, 18))
        # Pierna derecha
        pygame.draw.ellipse(surface, leg_color, (center_x + 1, center_y + 8, 6, 18))
        
        # Botas militares detalladas
        boot_color = (20, 20, 20)
        pygame.draw.ellipse(surface, boot_color, (center_x - 7, center_y + 22, 6, 6))
        pygame.draw.ellipse(surface, boot_color, (center_x + 1, center_y + 22, 6, 6))
        
        # Cordones de las botas
        lace_color = (100, 80, 60)
        for i in range(3):
            y_pos = center_y + 22 + i
            pygame.draw.line(surface, lace_color, (center_x - 5, y_pos), (center_x - 3, y_pos), 1)
            pygame.draw.line(surface, lace_color, (center_x + 3, y_pos), (center_x + 5, y_pos), 1)
        
        # Rifle de asalto M4 detallado
        gun_color = (40, 40, 40)
        # Cuerpo principal del arma
        gun_body = pygame.Rect(center_x + 8, center_y - 6, 18, 6)
        pygame.draw.rect(surface, gun_color, gun_body, border_radius=1)
        
        # Cañón
        barrel_rect = pygame.Rect(center_x + 24, center_y - 4, 10, 2)
        pygame.draw.rect(surface, gun_color, barrel_rect)
        
        # Supresor de fogonazo
        pygame.draw.rect(surface, (60, 60, 60), (center_x + 32, center_y - 4, 4, 2))
        
        # Culata
        stock_rect = pygame.Rect(center_x + 4, center_y - 4, 6, 4)
        pygame.draw.rect(surface, (80, 60, 40), stock_rect, border_radius=1)
        
        # Cargador
        mag_rect = pygame.Rect(center_x + 12, center_y + 2, 4, 10)
        pygame.draw.rect(surface, (30, 30, 30), mag_rect, border_radius=1)
        
        # Mira telescópica
        scope_rect = pygame.Rect(center_x + 15, center_y - 8, 8, 3)
        pygame.draw.rect(surface, (60, 60, 60), scope_rect, border_radius=1)
        pygame.draw.circle(surface, (100, 150, 200), (center_x + 19, center_y - 6), 2)
        
        # Manos realistas
        hand_color = (200, 150, 100)
        # Mano en el gatillo
        pygame.draw.circle(surface, hand_color, (center_x + 10, center_y - 2), 3)
        # Mano en la culata
        pygame.draw.circle(surface, hand_color, (center_x + 6, center_y + 2), 3)
        
        # Insignias y parches
        # Bandera en el hombro
        flag_rect = pygame.Rect(center_x - 12, center_y - 8, 6, 4)
        pygame.draw.rect(surface, (200, 0, 0), flag_rect)
        pygame.draw.rect(surface, (255, 255, 255), (center_x - 12, center_y - 7, 6, 1))
        pygame.draw.rect(surface, (0, 0, 200), (center_x - 12, center_y - 6, 6, 1))
        
        # Rango en el otro hombro
        rank_rect = pygame.Rect(center_x + 8, center_y - 8, 4, 3)
        pygame.draw.rect(surface, (255, 215, 0), rank_rect)
        
        return surface
    
    @staticmethod
    def create_detailed_soldier(size=48):
        """Soldado enemigo con uniforme rojo detallado"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra
        pygame.draw.ellipse(surface, (0, 0, 0, 80), 
                          (center_x - 12, center_y + 18, 24, 8))
        
        # Cuerpo (uniforme rojo enemigo)
        body_color = (140, 30, 30)
        body_rect = pygame.Rect(center_x - 9, center_y - 11, 18, 22)
        pygame.draw.ellipse(surface, body_color, body_rect)
        
        # Chaleco enemigo
        vest_color = (100, 20, 20)
        vest_rect = pygame.Rect(center_x - 7, center_y - 9, 14, 18)
        pygame.draw.rect(surface, vest_color, vest_rect, border_radius=2)
        
        # Detalles del chaleco
        pygame.draw.rect(surface, (80, 15, 15), (center_x - 6, center_y - 7, 12, 2))
        pygame.draw.rect(surface, (80, 15, 15), (center_x - 6, center_y - 3, 12, 2))
        pygame.draw.rect(surface, (80, 15, 15), (center_x - 6, center_y + 1, 12, 2))
        
        # Casco enemigo con distintivos
        helmet_color = (80, 15, 15)
        helmet_rect = pygame.Rect(center_x - 8, center_y - 16, 16, 11)
        pygame.draw.ellipse(surface, helmet_color, helmet_rect)
        
        # Símbolo enemigo (estrella roja)
        star_color = (255, 200, 0)
        pygame.draw.circle(surface, star_color, (center_x, center_y - 12), 4)
        # Estrella comunista
        star_points = []
        for i in range(5):
            angle = (i * 2 * math.pi / 5) - math.pi/2
            x = center_x + int(math.cos(angle) * 3)
            y = center_y - 12 + int(math.sin(angle) * 3)
            star_points.append((x, y))
        pygame.draw.polygon(surface, (200, 0, 0), star_points)
        
        # Brazos
        arm_color = body_color
        pygame.draw.ellipse(surface, arm_color, (center_x - 12, center_y - 4, 6, 14))
        pygame.draw.ellipse(surface, arm_color, (center_x + 6, center_y - 4, 6, 14))
        
        # Piernas
        leg_color = (120, 25, 25)
        pygame.draw.ellipse(surface, leg_color, (center_x - 6, center_y + 8, 5, 16))
        pygame.draw.ellipse(surface, leg_color, (center_x + 1, center_y + 8, 5, 16))
        
        # Botas enemigas
        pygame.draw.ellipse(surface, (40, 20, 20), (center_x - 6, center_y + 20, 5, 6))
        pygame.draw.ellipse(surface, (40, 20, 20), (center_x + 1, center_y + 20, 5, 6))
        
        # AK-47
        gun_color = (30, 30, 30)
        # Cuerpo curvo característico del AK
        pygame.draw.rect(surface, gun_color, (center_x + 6, center_y - 4, 16, 4), border_radius=1)
        # Cañón
        pygame.draw.rect(surface, gun_color, (center_x + 20, center_y - 2, 8, 2))
        # Cargador curvo
        pygame.draw.ellipse(surface, gun_color, (center_x + 10, center_y + 1, 3, 12))
        # Culata de madera
        pygame.draw.rect(surface, (139, 69, 19), (center_x + 2, center_y - 2, 6, 3))
        
        return surface
    
    @staticmethod
    def create_detailed_elite(size=48):
        """Soldado élite con armadura pesada"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra más grande
        pygame.draw.ellipse(surface, (0, 0, 0, 120), 
                          (center_x - 14, center_y + 18, 28, 10))
        
        # Armadura pesada (más grande)
        armor_color = (80, 10, 10)
        body_rect = pygame.Rect(center_x - 12, center_y - 14, 24, 28)
        pygame.draw.rect(surface, armor_color, body_rect, border_radius=4)
        
        # Placas de armadura superpuestas
        plate_colors = [(60, 5, 5), (40, 5, 5), (60, 5, 5)]
        for i, plate_color in enumerate(plate_colors):
            plate_rect = pygame.Rect(center_x - 10, center_y - 10 + i * 6, 20, 5)
            pygame.draw.rect(surface, plate_color, plate_rect, border_radius=2)
            # Remaches
            for j in range(4):
                rivet_x = center_x - 8 + j * 5
                pygame.draw.circle(surface, (100, 100, 100), (rivet_x, center_y - 8 + i * 6), 1)
        
        # Casco élite con visor HUD
        helmet_color = (50, 5, 5)
        helmet_rect = pygame.Rect(center_x - 10, center_y - 18, 20, 14)
        pygame.draw.rect(surface, helmet_color, helmet_rect, border_radius=3)
        
        # Visor futurista
        visor_colors = [(0, 100, 200), (0, 150, 255), (100, 200, 255)]
        for i, color in enumerate(visor_colors):
            visor_rect = pygame.Rect(center_x - 8 + i, center_y - 14, 16 - i * 2, 6)
            pygame.draw.rect(surface, color, visor_rect, border_radius=1)
        
        # Antena de comunicación
        pygame.draw.line(surface, (150, 150, 150), 
                        (center_x + 8, center_y - 16), (center_x + 12, center_y - 20), 2)
        pygame.draw.circle(surface, (255, 0, 0), (center_x + 12, center_y - 20), 2)
        
        # Hombros blindados masivos
        shoulder_color = armor_color
        pygame.draw.circle(surface, shoulder_color, (center_x - 15, center_y - 8), 8)
        pygame.draw.circle(surface, shoulder_color, (center_x + 15, center_y - 8), 8)
        
        # Detalles de los hombros
        pygame.draw.circle(surface, (100, 100, 100), (center_x - 15, center_y - 8), 3)
        pygame.draw.circle(surface, (100, 100, 100), (center_x + 15, center_y - 8), 3)
        
        # Piernas blindadas
        leg_armor_color = (70, 8, 8)
        pygame.draw.rect(surface, leg_armor_color, 
                        (center_x - 8, center_y + 10, 6, 16), border_radius=3)
        pygame.draw.rect(surface, leg_armor_color, 
                        (center_x + 2, center_y + 10, 6, 16), border_radius=3)
        
        # Rodilleras
        pygame.draw.circle(surface, (90, 90, 90), (center_x - 5, center_y + 14), 3)
        pygame.draw.circle(surface, (90, 90, 90), (center_x + 5, center_y + 14), 3)
        
        # Arma pesada (LMG)
        heavy_gun_color = (40, 40, 40)
        # Cuerpo del arma
        pygame.draw.rect(surface, heavy_gun_color, (center_x + 8, center_y - 6, 20, 8))
        # Cañón pesado
        pygame.draw.rect(surface, heavy_gun_color, (center_x + 26, center_y - 4, 12, 4))
        # Bípode
        pygame.draw.line(surface, heavy_gun_color, (center_x + 30, center_y + 2), (center_x + 28, center_y + 8), 2)
        pygame.draw.line(surface, heavy_gun_color, (center_x + 32, center_y + 2), (center_x + 34, center_y + 8), 2)
        # Cargador de tambor
        pygame.draw.circle(surface, (35, 35, 35), (center_x + 14, center_y + 4), 6)
        
        # Distintivos élite (múltiples estrellas doradas)
        star_color = (255, 215, 0)
        for i in range(3):
            star_x = center_x - 6 + i * 6
            pygame.draw.circle(surface, star_color, (star_x, center_y - 6), 2)
            # Pequeñas estrellas
            for j in range(5):
                angle = (j * 2 * math.pi / 5) - math.pi/2
                px = star_x + int(math.cos(angle) * 1.5)
                py = center_y - 6 + int(math.sin(angle) * 1.5)
                pygame.draw.circle(surface, (200, 150, 0), (px, py), 1)
        
        return surface
    
    @staticmethod
    def create_detailed_sniper(size=48):
        """Francotirador con camuflaje ghillie y rifle largo"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra difusa (camuflaje)
        pygame.draw.ellipse(surface, (0, 0, 0, 60), 
                          (center_x - 12, center_y + 18, 24, 8))
        
        # Cuerpo base camuflado
        camo_base = (60, 80, 40)
        body_rect = pygame.Rect(center_x - 8, center_y - 10, 16, 20)
        pygame.draw.ellipse(surface, camo_base, body_rect)
        
        # Patrón de camuflaje complejo
        camo_colors = [(40, 60, 20), (80, 100, 60), (45, 65, 25), (70, 90, 50)]
        
        # Crear patrón irregular
        random.seed(42)  # Seed fijo para consistencia
        for _ in range(25):
            x = random.randint(center_x - 10, center_x + 10)
            y = random.randint(center_y - 12, center_y + 12)
            color = random.choice(camo_colors)
            size_spot = random.randint(2, 6)
            pygame.draw.circle(surface, color, (x, y), size_spot)
        
        # Ghillie suit - elementos de vegetación
        vegetation_colors = [(60, 80, 40), (40, 60, 30), (70, 90, 50), (50, 70, 35)]
        for _ in range(20):
            x = random.randint(center_x - 12, center_x + 12)
            y = random.randint(center_y - 14, center_y + 16)
            color = random.choice(vegetation_colors)
            # Crear "hebras" de hierba
            for i in range(3):
                start_x = x + random.randint(-2, 2)
                start_y = y + i * 2
                end_x = start_x + random.randint(-3, 3)
                end_y = start_y + random.randint(3, 8)
                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 1)
        
        # Gorra de francotirador (boonie hat)
        hat_color = (40, 50, 30)
        hat_rect = pygame.Rect(center_x - 9, center_y - 14, 18, 10)
        pygame.draw.ellipse(surface, hat_color, hat_rect)
        
        # Ala del sombrero
        brim_rect = pygame.Rect(center_x - 11, center_y - 10, 22, 6)
        pygame.draw.ellipse(surface, (35, 45, 25), brim_rect)
        
        # Red de camuflaje en el sombrero
        for i in range(4):
            for j in range(4):
                net_x = center_x - 6 + i * 3
                net_y = center_y - 12 + j * 2
                pygame.draw.circle(surface, (30, 40, 20), (net_x, net_y), 1)
        
        # Cara parcialmente oculta
        face_color = (180, 140, 100)
        face_rect = pygame.Rect(center_x - 4, center_y - 8, 8, 6)
        pygame.draw.ellipse(surface, face_color, face_rect)
        
        # Pintura de camuflaje facial
        pygame.draw.line(surface, (40, 60, 30), (center_x - 3, center_y - 6), (center_x + 3, center_y - 7), 2)
        pygame.draw.line(surface, (40, 60, 30), (center_x - 2, center_y - 4), (center_x + 2, center_y - 5), 2)
        
        # Ojos alertas
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 2, center_y - 6), 1)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 2, center_y - 6), 1)
        pygame.draw.circle(surface, (50, 100, 50), (center_x - 2, center_y - 6), 1)
        pygame.draw.circle(surface, (50, 100, 50), (center_x + 2, center_y - 6), 1)
        
        # Brazos camuflados (delgados, sigilosos)
        arm_color = camo_base
        pygame.draw.ellipse(surface, arm_color, (center_x - 12, center_y - 2, 6, 12))
        pygame.draw.ellipse(surface, arm_color, (center_x + 6, center_y - 2, 6, 12))
        
        # Piernas en posición prone/agachado
        leg_color = camo_base
        pygame.draw.ellipse(surface, leg_color, (center_x - 6, center_y + 8, 5, 14))
        pygame.draw.ellipse(surface, leg_color, (center_x + 1, center_y + 6, 5, 16))
        
        # Rifle de francotirador de precisión
        rifle_color = (25, 25, 25)
        
        # Cuerpo del rifle (largo y delgado)
        rifle_body = pygame.Rect(center_x + 6, center_y - 3, 24, 4)
        pygame.draw.rect(surface, rifle_color, rifle_body, border_radius=1)
        
        # Cañón extra largo
        barrel_rect = pygame.Rect(center_x + 28, center_y - 2, 16, 2)
        pygame.draw.rect(surface, rifle_color, barrel_rect)
        
        # Supresor de sonido
        suppressor_rect = pygame.Rect(center_x + 42, center_y - 3, 6, 4)
        pygame.draw.rect(surface, (40, 40, 40), suppressor_rect, border_radius=2)
        
        # Mira telescópica avanzada
        scope_body = pygame.Rect(center_x + 12, center_y - 7, 12, 4)
        pygame.draw.rect(surface, (60, 60, 60), scope_body, border_radius=1)
        
        # Lentes de la mira
        pygame.draw.circle(surface, (100, 150, 200), (center_x + 15, center_y - 5), 2)
        pygame.draw.circle(surface, (120, 170, 220), (center_x + 21, center_y - 5), 2)
        
        # Reflejo en las lentes
        pygame.draw.circle(surface, (200, 220, 255), (center_x + 15, center_y - 6), 1)
        pygame.draw.circle(surface, (200, 220, 255), (center_x + 21, center_y - 6), 1)
        
        # Bípode desplegado
        bipod_color = (80, 80, 80)
        pygame.draw.line(surface, bipod_color, (center_x + 18, center_y + 1), (center_x + 14, center_y + 12), 2)
        pygame.draw.line(surface, bipod_color, (center_x + 22, center_y + 1), (center_x + 26, center_y + 12), 2)
        
        # Culata de madera premium
        stock_rect = pygame.Rect(center_x + 2, center_y - 2, 8, 4)
        pygame.draw.rect(surface, (100, 60, 30), stock_rect, border_radius=1)
        
        # Vetas de la madera
        pygame.draw.line(surface, (80, 50, 25), (center_x + 3, center_y - 1), (center_x + 8, center_y), 1)
        pygame.draw.line(surface, (80, 50, 25), (center_x + 3, center_y + 1), (center_x + 9, center_y + 1), 1)
        
        # Manos con guantes tácticos
        glove_color = (40, 60, 30)
        pygame.draw.circle(surface, glove_color, (center_x + 8, center_y + 1), 3)  # Mano en gatillo
        pygame.draw.circle(surface, glove_color, (center_x + 4, center_y + 2), 3)   # Mano en culata
        
        # Elementos adicionales del ghillie
        for _ in range(15):
            x = random.randint(center_x - 14, center_x + 14)
            y = random.randint(center_y - 16, center_y + 20)
            color = random.choice(vegetation_colors)
            # Crear elementos de vegetación más largos
            length = random.randint(4, 10)
            angle = random.uniform(0, 2 * math.pi)
            end_x = x + int(math.cos(angle) * length)
            end_y = y + int(math.sin(angle) * length)
            pygame.draw.line(surface, color, (x, y), (end_x, end_y), 1)
        
        return surface
    
    @staticmethod
    def create_detailed_kamikaze(size=48):
        """Kamikaze con explosivos detallados y expresión maniaca"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra nerviosa (temblando)
        pygame.draw.ellipse(surface, (0, 0, 0, 100), 
                          (center_x - 12, center_y + 18, 24, 8))
        
        # Cuerpo (uniforme deteriorado)
        body_color = (120, 80, 40)
        body_rect = pygame.Rect(center_x - 9, center_y - 10, 18, 20)
        pygame.draw.ellipse(surface, body_color, body_rect)
        
        # Ropa rasgada y desgastada
        tear_color = (100, 60, 30)
        # Rasgaduras
        pygame.draw.line(surface, tear_color, (center_x - 7, center_y - 5), (center_x - 4, center_y - 2), 2)
        pygame.draw.line(surface, tear_color, (center_x + 3, center_y + 1), (center_x + 6, center_y + 4), 2)
        
        # Chaleco de explosivos súper detallado
        vest_color = (200, 100, 0)
        vest_rect = pygame.Rect(center_x - 10, center_y - 8, 20, 16)
        pygame.draw.rect(surface, vest_color, vest_rect, border_radius=2)
        
        # Múltiples explosivos (TNT y C4)
        explosive_positions = [
            (center_x - 8, center_y - 6), (center_x - 4, center_y - 7), (center_x, center_y - 6),
            (center_x + 4, center_y - 7), (center_x + 8, center_y - 6),
            (center_x - 6, center_y - 2), (center_x + 6, center_y - 2),
            (center_x - 8, center_y + 2), (center_x - 4, center_y + 3), (center_x, center_y + 2),
            (center_x + 4, center_y + 3), (center_x + 8, center_y + 2)
        ]
        
        for i, (x, y) in enumerate(explosive_positions):
            if i % 3 == 0:  # TNT (rojo)
                explosive_color = (220, 20, 20)
                pygame.draw.rect(surface, explosive_color, (x - 1, y - 4, 3, 8), border_radius=1)
                # Etiqueta TNT
                pygame.draw.rect(surface, (255, 255, 255), (x - 1, y - 1, 3, 2))
            elif i % 3 == 1:  # C4 (gris)
                explosive_color = (100, 100, 100)
                pygame.draw.rect(surface, explosive_color, (x - 1, y - 3, 3, 6), border_radius=1)
            else:  # Granada (verde militar)
                explosive_color = (60, 80, 40)
                pygame.draw.circle(surface, explosive_color, (x, y), 2)
                # Anilla
                pygame.draw.circle(surface, (200, 200, 200), (x, y - 3), 1)
        
        # Cables y circuitos complejos
        wire_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i in range(len(explosive_positions) - 1):
            start_pos = explosive_positions[i]
            end_pos = explosive_positions[i + 1]
            wire_color = wire_colors[i % len(wire_colors)]
            pygame.draw.line(surface, wire_color, start_pos, end_pos, 1)
        
        # Circuito central (detonador principal)
        circuit_rect = pygame.Rect(center_x - 3, center_y - 1, 6, 4)
        pygame.draw.rect(surface, (50, 50, 50), circuit_rect)
        # LED parpadeante
        pygame.draw.circle(surface, (255, 0, 0), (center_x, center_y + 1), 2)
        # Pequeños componentes
        pygame.draw.rect(surface, (200, 200, 0), (center_x - 2, center_y, 1, 1))
        pygame.draw.rect(surface, (0, 200, 0), (center_x + 1, center_y, 1, 1))
        
        # Cabeza sin casco (pelo alborotado)
        head_color = (200, 150, 100)
        pygame.draw.circle(surface, head_color, (center_x, center_y - 12), 8)
        
        # Pelo completamente loco
        hair_color = (60, 40, 20)
        hair_positions = []
        for i in range(20):
            angle = (i / 20) * 2 * math.pi + random.uniform(-0.5, 0.5)
            length = random.randint(4, 12)
            start_x = center_x + int(math.cos(angle) * 7)
            start_y = center_y - 12 + int(math.sin(angle) * 7)
            end_x = start_x + int(math.cos(angle) * length)
            end_y = start_y + int(math.sin(angle) * length)
            pygame.draw.line(surface, hair_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Cara completamente loca
        # Ojos desorbitados
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 3, center_y - 13), 3)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 3, center_y - 13), 3)
        # Pupilas dilatadas y desiguales
        pygame.draw.circle(surface, (255, 0, 0), (center_x - 3, center_y - 13), 2)
        pygame.draw.circle(surface, (255, 0, 0), (center_x + 3, center_y - 12), 1)
        
        # Sonrisa maniaca gigante
        smile_points = []
        for i in range(7):
            angle = (i / 6) * math.pi
            x = center_x + int(math.cos(angle + math.pi) * 4)
            y = center_y - 8 + int(math.sin(angle + math.pi) * 2)
            smile_points.append((x, y))
        if len(smile_points) >= 2:
            pygame.draw.lines(surface, (0, 0, 0), False, smile_points, 2)
        
        # Dientes visibles
        for i in range(4):
            tooth_x = center_x - 2 + i
            pygame.draw.rect(surface, (255, 255, 255), (tooth_x, center_y - 9, 1, 2))
        
        # Detonador en la mano (muy detallado)
        detonator_base = pygame.Rect(center_x - 14, center_y + 2, 6, 8)
        pygame.draw.rect(surface, (150, 150, 150), detonator_base, border_radius=1)
        
        # Botón rojo GIGANTE
        pygame.draw.circle(surface, (255, 0, 0), (center_x - 11, center_y + 4), 3)
        pygame.draw.circle(surface, (200, 0, 0), (center_x - 11, center_y + 4), 2)
        pygame.draw.circle(surface, (255, 100, 100), (center_x - 12, center_y + 3), 1)  # Brillo
        
        # Etiqueta de peligro
        pygame.draw.rect(surface, (255, 255, 0), (center_x - 13, center_y + 6, 4, 2))
        # Símbolo de radiación pequeño
        pygame.draw.circle(surface, (0, 0, 0), (center_x - 11, center_y + 7), 1)
        
        # Antena del detonador
        pygame.draw.line(surface, (200, 200, 200), 
                        (center_x - 8, center_y + 2), (center_x - 6, center_y - 2), 1)
        
        # Timer digital visible
        pygame.draw.rect(surface, (0, 255, 0), (center_x - 13, center_y + 1, 3, 1))
        
        # Brazos temblorosos
        arm_color = body_color
        # Brazo izquierdo (sosteniendo detonador)
        pygame.draw.ellipse(surface, arm_color, (center_x - 16, center_y, 8, 12))
        # Brazo derecho (agitándose)
        pygame.draw.ellipse(surface, arm_color, (center_x + 8, center_y - 2, 8, 14))
        
        # Piernas en movimiento (corriendo/temblando)
        leg_color = (100, 60, 30)
        # Pierna izquierda (levantada)
        pygame.draw.ellipse(surface, leg_color, (center_x - 6, center_y + 6, 5, 12))
        # Pierna derecha (en el suelo)
        pygame.draw.ellipse(surface, leg_color, (center_x + 1, center_y + 8, 5, 14))
        
        # Botas desgastadas
        pygame.draw.ellipse(surface, (40, 20, 10), (center_x - 6, center_y + 16, 5, 4))
        pygame.draw.ellipse(surface, (40, 20, 10), (center_x + 1, center_y + 20, 5, 4))
        
        # Efectos de pánico: gotas de sudor
        sweat_color = (200, 220, 255)
        sweat_positions = [(center_x - 5, center_y - 8), (center_x + 4, center_y - 9), (center_x - 1, center_y - 6)]
        for pos in sweat_positions:
            pygame.draw.circle(surface, sweat_color, pos, 1)
        
        # Humo saliendo de los explosivos
        smoke_color = (100, 100, 100, 150)
        for i in range(5):
            smoke_x = center_x + random.randint(-8, 8)
            smoke_y = center_y - 8 + random.randint(-2, 2)
            pygame.draw.circle(surface, (120, 120, 120), (smoke_x, smoke_y), random.randint(1, 2))
        
        return surface
    
    @staticmethod
    def create_detailed_officer(size=48):
        """Oficial con uniforme elegante y múltiples insignias"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center_x, center_y = size // 2, size // 2
        
        # Sombra elegante
        pygame.draw.ellipse(surface, (0, 0, 0, 110), 
                          (center_x - 12, center_y + 18, 24, 8))
        
        # Cuerpo (uniforme de oficial verde oscuro premium)
        uniform_color = (40, 80, 40)
        body_rect = pygame.Rect(center_x - 10, center_y - 11, 20, 22)
        pygame.draw.rect(surface, uniform_color, body_rect, border_radius=3)
        
        # Casaca militar de gala con solapa
        jacket_color = (30, 60, 30)
        jacket_rect = pygame.Rect(center_x - 9, center_y - 10, 18, 18)
        pygame.draw.rect(surface, jacket_color, jacket_rect, border_radius=3)
        
        # Solapas de la casaca
        lapel_color = (20, 40, 20)
        # Solapa izquierda
        lapel_points_left = [
            (center_x - 9, center_y - 10),
            (center_x - 2, center_y - 10),
            (center_x - 4, center_y - 6),
            (center_x - 9, center_y - 6)
        ]
        pygame.draw.polygon(surface, lapel_color, lapel_points_left)
        
        # Solapa derecha
        lapel_points_right = [
            (center_x + 2, center_y - 10),
            (center_x + 9, center_y - 10),
            (center_x + 9, center_y - 6),
            (center_x + 4, center_y - 6)
        ]
        pygame.draw.polygon(surface, lapel_color, lapel_points_right)
        
        # Doble fila de botones dorados ornamentados
        button_color = (255, 215, 0)
        button_positions = [
            # Fila izquierda
            (center_x - 3, center_y - 8), (center_x - 3, center_y - 5),
            (center_x - 3, center_y - 2), (center_x - 3, center_y + 1),
            # Fila derecha
            (center_x + 3, center_y - 8), (center_x + 3, center_y - 5),
            (center_x + 3, center_y - 2), (center_x + 3, center_y + 1)
        ]
        
        for pos in button_positions:
            pygame.draw.circle(surface, button_color, pos, 2)
            pygame.draw.circle(surface, (200, 170, 0), pos, 1)  # Brillo interno
        
        # Charreteras elaboradas (hombreras)
        shoulder_base = (255, 215, 0)
        shoulder_detail = (200, 170, 0)
        
        # Charretera izquierda
        pygame.draw.rect(surface, shoulder_base, 
                        (center_x - 12, center_y - 10, 4, 8), border_radius=1)
        # Flecos dorados
        for i in range(6):
            fringe_y = center_y - 9 + i
            pygame.draw.line(surface, shoulder_detail, 
                           (center_x - 12, fringe_y), (center_x - 14, fringe_y + 2), 1)
        
        # Charretera derecha
        pygame.draw.rect(surface, shoulder_base, 
                        (center_x + 8, center_y - 10, 4, 8), border_radius=1)
        for i in range(6):
            fringe_y = center_y - 9 + i
            pygame.draw.line(surface, shoulder_detail, 
                           (center_x + 12, fringe_y), (center_x + 14, fringe_y + 2), 1)
        
        # Gorra de oficial de alto rango
        cap_color = (25, 50, 25)
        cap_rect = pygame.Rect(center_x - 9, center_y - 18, 18, 12)
        pygame.draw.ellipse(surface, cap_color, cap_rect)
        
        # Banda dorada de la gorra
        pygame.draw.rect(surface, button_color, (center_x - 8, center_y - 12, 16, 2))
        
        # Visera de la gorra (pulida)
        visor_color = (15, 30, 15)
        visor_rect = pygame.Rect(center_x - 8, center_y - 10, 16, 4)
        pygame.draw.ellipse(surface, visor_color, visor_rect)
        # Brillo en la visera
        pygame.draw.ellipse(surface, (50, 80, 50), (center_x - 6, center_y - 9, 12, 2))
        
        # Insignia de oficial (águila compleja)
        eagle_base = (255, 215, 0)
        eagle_detail = (200, 170, 0)
        
        # Cuerpo del águila
        pygame.draw.circle(surface, eagle_base, (center_x, center_y - 13), 4)
        
        # Alas extendidas
        wing_points_left = [
            (center_x - 4, center_y - 13),
            (center_x - 8, center_y - 11),
            (center_x - 6, center_y - 15),
            (center_x - 3, center_y - 14)
        ]
        pygame.draw.polygon(surface, eagle_base, wing_points_left)
        
        wing_points_right = [
            (center_x + 4, center_y - 13),
            (center_x + 8, center_y - 11),
            (center_x + 6, center_y - 15),
            (center_x + 3, center_y - 14)
        ]
        pygame.draw.polygon(surface, eagle_base, wing_points_right)
        
        # Detalles del águila
        pygame.draw.circle(surface, eagle_detail, (center_x, center_y - 13), 2)
        pygame.draw.circle(surface, (255, 0, 0), (center_x, center_y - 14), 1)  # Ojo del águila
        
        # Cara seria y autoritaria
        face_color = (200, 150, 100)
        pygame.draw.ellipse(surface, face_color, (center_x - 5, center_y - 9, 10, 8))
        
        # Ojos serios y penetrantes
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 2, center_y - 7), 2)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 2, center_y - 7), 2)
        pygame.draw.circle(surface, (50, 50, 50), (center_x - 2, center_y - 7), 1)
        pygame.draw.circle(surface, (50, 50, 50), (center_x + 2, center_y - 7), 1)
        
        # Cejas fruncidas
        pygame.draw.line(surface, (100, 70, 50), (center_x - 3, center_y - 8), (center_x - 1, center_y - 9), 2)
        pygame.draw.line(surface, (100, 70, 50), (center_x + 1, center_y - 9), (center_x + 3, center_y - 8), 2)
        
        # Bigote militar elaborado
        mustache_color = (80, 60, 40)
        mustache_points = [
            (center_x - 3, center_y - 5),
            (center_x - 1, center_y - 4),
            (center_x + 1, center_y - 4),
            (center_x + 3, center_y - 5)
        ]
        pygame.draw.lines(surface, mustache_color, False, mustache_points, 2)
        
        # Boca seria
        pygame.draw.line(surface, (150, 100, 70), (center_x - 2, center_y - 3), (center_x + 2, center_y - 3), 2)
        
        # Brazos con galones y decoraciones
        arm_color = uniform_color
        # Brazo izquierdo
        pygame.draw.ellipse(surface, arm_color, (center_x - 14, center_y - 4, 8, 16))
        # Brazo derecho
        pygame.draw.ellipse(surface, arm_color, (center_x + 6, center_y - 4, 8, 16))
        
        # Galones de rango en las mangas
        stripe_color = (255, 215, 0)
        # Galones izquierdo
        for i in range(4):
            stripe_y = center_y - 2 + i * 2
            pygame.draw.line(surface, stripe_color, 
                           (center_x - 13, stripe_y), (center_x - 9, stripe_y), 2)
        
        # Galones derecho
        for i in range(4):
            stripe_y = center_y - 2 + i * 2
            pygame.draw.line(surface, stripe_color, 
                           (center_x + 9, stripe_y), (center_x + 13, stripe_y), 2)
        
        # Guantes blancos ceremoniosos
        glove_color = (240, 240, 240)
        pygame.draw.circle(surface, glove_color, (center_x - 16, center_y + 4), 4)
        pygame.draw.circle(surface, glove_color, (center_x + 16, center_y + 4), 4)
        
        # Detalles de los guantes
        pygame.draw.circle(surface, (220, 220, 220), (center_x - 16, center_y + 4), 2)
        pygame.draw.circle(surface, (220, 220, 220), (center_x + 16, center_y + 4), 2)
        
        # Pistola de oficial (Luger o similar)
        pistol_color = (60, 60, 60)
        pistol_rect = pygame.Rect(center_x + 10, center_y - 3, 8, 5)
        pygame.draw.rect(surface, pistol_color, pistol_rect, border_radius=1)
        
        # Cañón de la pistola
        pygame.draw.rect(surface, pistol_color, (center_x + 16, center_y - 1, 4, 1))
        
        # Empuñadura ornamentada
        pygame.draw.rect(surface, (100, 60, 30), (center_x + 10, center_y + 2, 3, 4))
        
        # Bastón de mando elaborado
        baton_color = (139, 69, 19)
        # Vara del bastón
        pygame.draw.rect(surface, baton_color, (center_x - 18, center_y - 6, 2, 16))
        
        # Pomo dorado del bastón
        pygame.draw.circle(surface, (255, 215, 0), (center_x - 17, center_y - 6), 3)
        # Detalles del pomo
        pygame.draw.circle(surface, (200, 170, 0), (center_x - 17, center_y - 6), 2)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 18, center_y - 7), 1)  # Brillo
        
        # Regatón del bastón
        pygame.draw.circle(surface, (150, 150, 150), (center_x - 17, center_y + 10), 2)
        
        # Piernas con pantalones de gala
        leg_color = (35, 70, 35)
        # Pierna izquierda
        pygame.draw.rect(surface, leg_color, 
                        (center_x - 7, center_y + 8, 6, 16), border_radius=3)
        # Pierna derecha
        pygame.draw.rect(surface, leg_color, 
                        (center_x + 1, center_y + 8, 6, 16), border_radius=3)
        
        # Franjas doradas en los pantalones
        stripe_width = 1
        pygame.draw.line(surface, (255, 215, 0), 
                        (center_x - 5, center_y + 10), (center_x - 5, center_y + 22), stripe_width)
        pygame.draw.line(surface, (255, 215, 0), 
                        (center_x + 3, center_y + 10), (center_x + 3, center_y + 22), stripe_width)
        
        # Botas militares de gala (pulidas)
        boot_color = (20, 20, 20)
        # Bota izquierda
        pygame.draw.rect(surface, boot_color, 
                        (center_x - 7, center_y + 22, 6, 6), border_radius=2)
        # Bota derecha
        pygame.draw.rect(surface, boot_color, 
                        (center_x + 1, center_y + 22, 6, 6), border_radius=2)
        
        # Brillo intenso en las botas
        pygame.draw.rect(surface, (120, 120, 120), 
                        (center_x - 6, center_y + 22, 4, 2))
        pygame.draw.rect(surface, (120, 120, 120), 
                        (center_x + 2, center_y + 22, 4, 2))
        
        # Espuelas
        pygame.draw.circle(surface, (180, 180, 180), (center_x - 4, center_y + 26), 2)
        pygame.draw.circle(surface, (180, 180, 180), (center_x + 4, center_y + 26), 2)
        
        # Medallas y condecoraciones en el pecho
        medal_positions = [
            (center_x - 5, center_y - 4), (center_x - 2, center_y - 4), (center_x + 1, center_y - 4),
            (center_x - 5, center_y - 1), (center_x - 2, center_y - 1), (center_x + 1, center_y - 1),
            (center_x - 3, center_y + 2)  # Medalla principal más grande
        ]
        
        medal_colors = [
            (255, 215, 0),  # Oro
            (192, 192, 192),  # Plata
            (205, 127, 50),  # Bronce
            (255, 215, 0),  # Oro
            (192, 192, 192),  # Plata
            (205, 127, 50),  # Bronce
            (255, 0, 0)  # Rojo especial
        ]
        
        for i, (pos, color) in enumerate(zip(medal_positions, medal_colors)):
            if i == 6:  # Medalla principal
                pygame.draw.circle(surface, color, pos, 3)
                pygame.draw.circle(surface, (255, 255, 255), pos, 2)
                pygame.draw.circle(surface, color, pos, 1)
            else:
                pygame.draw.circle(surface, color, pos, 2)
                pygame.draw.circle(surface, (255, 255, 255), (pos[0], pos[1] - 1), 1)
        
        # Cordones y cintas de las medallas
        ribbon_color = (150, 0, 0)
        for i in range(6):
            start_y = center_y - 6
            end_pos = medal_positions[i]
            pygame.draw.line(surface, ribbon_color, 
                           (end_pos[0], start_y), end_pos, 1)
        
        return surface
    
    @staticmethod
    def create_detailed_bullet(size=12):
        """Bala mejorada con estela y detalles"""
        surface = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        
        # Cuerpo principal de la bala (dorado)
        bullet_color = (255, 215, 0)
        bullet_rect = pygame.Rect(size, size//3, size//2, size//3)
        pygame.draw.ellipse(surface, bullet_color, bullet_rect)
        
        # Punta de la bala (plateado)
        tip_points = [
            (size + size//2, size//2),
            (size + size//1.2, size//3),
            (size + size//1.2, size * 2//3)
        ]
        pygame.draw.polygon(surface, (200, 200, 200), tip_points)
        
        # Base de la bala (bronce)
        base_rect = pygame.Rect(size - 2, size//3, 4, size//3)
        pygame.draw.rect(surface, (180, 120, 60), base_rect)
        
        # Estela de movimiento
        trail_colors = [
            (255, 255, 0, 150),
            (255, 200, 0, 100), 
            (255, 150, 0, 50),
            (255, 100, 0, 25)
        ]
        
        for i, color in enumerate(trail_colors):
            trail_rect = pygame.Rect(size - (i + 1) * 4, size//2 - 1, 4, 2)
            trail_surface = pygame.Surface((4, 2), pygame.SRCALPHA)
            trail_surface.fill(color)
            surface.blit(trail_surface, trail_rect)
        
        # Brillo en la punta
        pygame.draw.circle(surface, (255, 255, 255), 
                         (size + size//1.5, size//2), 1)
        
        return surface
    
    @staticmethod
    def create_detailed_powerup(powerup_type, size=32):
        """Power-ups mejorados con efectos animados"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Aura brillante multicapa
        aura_layers = 5
        for layer in range(aura_layers, 0, -1):
            alpha = int(30 * (layer / aura_layers))
            radius = center + layer * 2
            
            aura_surface = pygame.Surface((size + layer * 4, size + layer * 4), pygame.SRCALPHA)
            
            if powerup_type == "health":
                color = (0, 255, 0, alpha)
            elif powerup_type == "ammo":
                color = (255, 255, 0, alpha)
            else:  # speed
                color = (0, 100, 255, alpha)
            
            pygame.draw.circle(aura_surface, color, 
                             (aura_surface.get_width()//2, aura_surface.get_height()//2), 
                             radius)
            
            # Centrar la aura en la superficie principal
            blit_x = (size - aura_surface.get_width()) // 2
            blit_y = (size - aura_surface.get_height()) // 2
            surface.blit(aura_surface, (blit_x, blit_y))
        
        # Base del power-up con gradiente
        if powerup_type == "health":
            base_colors = [(0, 150, 0), (0, 200, 0), (0, 255, 0)]
            symbol_color = (255, 255, 255)
        elif powerup_type == "ammo":
            base_colors = [(150, 150, 0), (200, 200, 0), (255, 255, 0)]
            symbol_color = (100, 50, 0)
        else:  # speed
            base_colors = [(0, 50, 150), (0, 75, 200), (0, 100, 255)]
            symbol_color = (255, 255, 255)
        
        # Círculo con gradiente
        for i, color in enumerate(base_colors):
            radius = center - i * 2
            pygame.draw.circle(surface, color, (center, center), radius)
        
        # Borde brillante
        pygame.draw.circle(surface, (255, 255, 255), (center, center), center - 1, 2)
        
        # Símbolos específicos mejorados
        if powerup_type == "health":
            # Cruz médica 3D
            # Sombra de la cruz
            shadow_offset = 1
            pygame.draw.rect(surface, (0, 100, 0), 
                           (center - 8 + shadow_offset, center - 3 + shadow_offset, 16, 6), border_radius=2)
            pygame.draw.rect(surface, (0, 100, 0), 
                           (center - 3 + shadow_offset, center - 8 + shadow_offset, 6, 16), border_radius=2)
            
            # Cruz principal
            pygame.draw.rect(surface, symbol_color, 
                           (center - 8, center - 3, 16, 6), border_radius=2)
            pygame.draw.rect(surface, symbol_color, 
                           (center - 3, center - 8, 6, 16), border_radius=2)
            
            # Brillo en la cruz
            pygame.draw.rect(surface, (255, 255, 255), 
                           (center - 7, center - 2, 14, 2))
            pygame.draw.rect(surface, (255, 255, 255), 
                           (center - 2, center - 7, 2, 14))
            
        elif powerup_type == "ammo":
            # Caja de munición detallada
            box_color = symbol_color
            
            # Sombra de la caja
            pygame.draw.rect(surface, (80, 40, 0), 
                           (center - 7, center - 5, 14, 10), border_radius=2)
            
            # Caja principal
            pygame.draw.rect(surface, box_color, 
                           (center - 8, center - 6, 14, 10), border_radius=2)
            
            # Tapa de la caja
            pygame.draw.rect(surface, (120, 60, 0), 
                           (center - 8, center - 6, 14, 3), border_radius=2)
            
            # Detalles de munición
            for i in range(3):
                bullet_x = center - 4 + i * 4
                # Casquillos
                pygame.draw.rect(surface, (180, 120, 60), 
                               (bullet_x - 1, center - 3, 2, 6))
                # Puntas
                pygame.draw.circle(surface, (200, 200, 200), 
                                 (bullet_x, center - 4), 2)
            
            # Etiqueta "AMMO"
            pygame.draw.rect(surface, (255, 255, 255), 
                           (center - 6, center + 2, 12, 2))
            
        else:  # speed
            # Rayo de velocidad con efectos
            # Múltiples rayos para efecto de movimiento
            for offset in range(3):
                lightning_alpha = 255 - offset * 80
                lightning_color = (*symbol_color[:3], lightning_alpha)
                
                lightning_points = [
                    (center + 4 - offset, center - 8),
                    (center - 4 - offset, center - 1),
                    (center + 2 - offset, center - 1),
                    (center - 6 - offset, center + 8),
                    (center + 0 - offset, center + 1),
                    (center - 2 - offset, center + 1)
                ]
                
                # Crear superficie temporal para alpha
                lightning_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.polygon(lightning_surface, lightning_color, lightning_points)
                surface.blit(lightning_surface, (0, 0))
            
            # Rayo principal brillante
            main_lightning_points = [
                (center + 4, center - 8),
                (center - 4, center - 1),
                (center + 2, center - 1),
                (center - 6, center + 8),
                (center + 0, center + 1),
                (center - 2, center + 1)
            ]
            pygame.draw.polygon(surface, symbol_color, main_lightning_points)
            
            # Brillo interno
            inner_lightning_points = [
                (center + 2, center - 6),
                (center - 2, center - 1),
                (center + 1, center - 1),
                (center - 4, center + 6),
                (center - 1, center + 1),
                (center - 1, center + 1)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), inner_lightning_points)
        
        # Puntos de luz giratorios
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            spark_x = center + int(math.cos(angle) * (center + 5))
            spark_y = center + int(math.sin(angle) * (center + 5))
            
            # Verificar que esté dentro de los límites
            if 0 <= spark_x < size and 0 <= spark_y < size:
                pygame.draw.circle(surface, (255, 255, 255), (spark_x, spark_y), 1)
        
        return surface
    
    @staticmethod
    def create_explosion_animation(frames=8, size=64):
        """Crea una animación de explosión detallada"""
        animation_frames = []
        
        for frame in range(frames):
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            center = size // 2
            
            # Progreso de la animación (0 a 1)
            progress = frame / (frames - 1)
            
            # Radio de la explosión
            max_radius = size // 2
            current_radius = int(max_radius * (0.3 + progress * 0.7))
            
            # Colores que evolucionan con el tiempo
            if progress < 0.2:
                # Destello inicial blanco
                colors = [(255, 255, 255), (255, 255, 200), (255, 200, 100)]
                alphas = [255, 200, 150]
            elif progress < 0.5:
                # Explosión naranja/amarilla
                colors = [(255, 200, 0), (255, 150, 0), (255, 100, 0)]
                alphas = [240, 180, 120]
            elif progress < 0.8:
                # Transición a rojo
                colors = [(255, 100, 0), (200, 50, 0), (150, 25, 0)]
                alphas = [200, 140, 80]
            else:
                # Humo final
                colors = [(100, 50, 25), (80, 40, 20), (60, 30, 15)]
                alphas = [160, 100, 60]
            
            # Dibujar múltiples capas de explosión
            for i, (color, alpha) in enumerate(zip(colors, alphas)):
                layer_radius = current_radius - i * 5
                if layer_radius > 0:
                    # Crear superficie temporal con alpha
                    layer_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    
                    # Círculo principal
                    pygame.draw.circle(layer_surface, (*color, alpha), 
                                     (center, center), layer_radius)
                    
                    # Efectos adicionales según el frame
                    if frame < 4:  # Primeros frames: chispas
                        for j in range(12):
                            angle = (j / 12) * 2 * math.pi
                            spark_distance = layer_radius + random.randint(5, 15)
                            spark_x = center + int(math.cos(angle) * spark_distance)
                            spark_y = center + int(math.sin(angle) * spark_distance)
                            
                            if 0 <= spark_x < size and 0 <= spark_y < size:
                                spark_size = random.randint(1, 3)
                                pygame.draw.circle(layer_surface, 
                                                 (255, 255, 0, alpha), 
                                                 (spark_x, spark_y), spark_size)
                    
                    elif frame >= 4:  # Frames finales: humo
                        for j in range(8):
                            angle = (j / 8) * 2 * math.pi + progress * math.pi
                            smoke_distance = layer_radius + j * 3
                            smoke_x = center + int(math.cos(angle) * smoke_distance)
                            smoke_y = center + int(math.sin(angle) * smoke_distance) - j * 2
                            
                            if 0 <= smoke_x < size and 0 <= smoke_y < size:
                                smoke_radius = 3 + j
                                smoke_alpha = max(0, alpha - j * 20)
                                pygame.draw.circle(layer_surface, 
                                                 (60, 60, 60, smoke_alpha), 
                                                 (smoke_x, smoke_y), smoke_radius)
                    
                    surface.blit(layer_surface, (0, 0))
            
            # Efectos especiales para frames específicos
            if frame == 1:  # Segundo frame: anillo de shock wave
                pygame.draw.circle(surface, (255, 255, 255, 100), 
                                 (center, center), current_radius + 10, 3)
            
            animation_frames.append(surface)
        
        return animation_frames

# Función principal para configurar todo
def setup_enhanced_sprites():
    """Función principal para configurar los sprites mejorados"""
    return EnhancedSprites.setup_enhanced_sprites()

if __name__ == "__main__":
    # Ejecutar si se llama directamente
    sprites_path = setup_enhanced_sprites()
    print(f"✅ Sprites mejorados listos en: {sprites_path}")