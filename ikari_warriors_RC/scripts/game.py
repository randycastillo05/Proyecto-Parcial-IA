import pygame
import random
import math
import os
from scripts.player import Player
from scripts.enemy import Enemy  # Cambiar a enemy en lugar de enemy_updated
from scripts.bullet import Bullet, Explosion, PowerUp, BulletManager
from scripts.utils.constants import *
from scripts.utils.resources import ResourceManager
from scripts.ai.pathfinding import Grid, AStar
from scripts.utils.audio_manager import get_audio_manager
from scripts.utils.particle_system import ParticleSystem
from scripts.utils.enhanced_visual import VisualEffects, WeatherEffects
from scripts.utils.game_feel import CameraSystem, CombatEffects, GameFeedback, UIEffects
from scripts.utils.progression_system import ProgressionSystem, ComboSystem, WaveManager


class Game:
    """Clase principal que maneja el estado del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.PLAYING
        self.resource_manager = ResourceManager()
        
        # Sistemas del juego
        self.audio_manager = get_audio_manager()
        self.particle_system = ParticleSystem()
        self.camera = CameraSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_feedback = GameFeedback()
        self.weather_effects = WeatherEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Sistemas de progresión
        self.progression = ProgressionSystem()
        self.combo_system = ComboSystem()
        self.wave_manager = WaveManager()
        
        # Superficies de renderizado
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.ui_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Fondo mejorado
        self.background = VisualEffects.create_gradient_background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.create_tiled_floor()
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        
        # Crear grid para pathfinding
        grid_width = SCREEN_WIDTH // TILE_SIZE
        grid_height = SCREEN_HEIGHT // TILE_SIZE
        self.grid = Grid(grid_width, grid_height, TILE_SIZE)
        self.pathfinder = AStar(self.grid)
        
        # Crear gestor de balas
        self.bullet_manager = BulletManager(self.bullets, self.explosions)
        
        # Crear mapa mejorado
        self.create_enhanced_map()
        
        # Crear jugador
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.game = self
        self.all_sprites.add(self.player)
        
        # Aplicar stats de progresión al jugador
        self.apply_progression_stats()
        
        # Variables de juego
        self.score = 0
        self.wave = 0
        self.enemies_remaining = 0
        self.spawn_timer = 0
        self.spawn_queue = []
        
        # Efectos visuales
        self.screen_effects = []
        self.damage_vignette = VisualEffects.create_damage_vignette(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.damage_vignette_alpha = 0
        
        # Variables para debug
        self.show_pathfinding = False
        self.show_debug_info = False
        self.show_fps = True
        
        # Inicializar gamepad
        self.init_gamepad()
        
        # Música y sonidos
        self.init_audio()
        
        # Iniciar primera oleada
        self.start_next_wave()

        self.screen_shake=0
        self.add_screen_shake

        self.spawn_cooldown=2.0
        self.max_enemies_per_wave=10

        self.paused= False

    def add_screen_shake(self, intensity, duration):
        self.screen_shake = max(self.screen_shake, duration)
        self.screen_shake_intensity = max(self.screen_shake_intensity,intensity  )


    def update_screen_shake(self, dt):
        if self.screen_shake > 0:
            self.screen_shake -= dt
            if self.screen_shake <= 0:
                self.screen_shake = 0
                self.screen_shake_intensity = 0
        
    def create_test_map(self):
        """Crea un mapa más interesante con obstáculos"""
        # Bordes del mapa
        for x in range(self.grid.width):
            self.grid.set_walkable(x, 0, False)
            self.grid.set_walkable(x, self.grid.height - 1, False)
        
        for y in range(self.grid.height):
            self.grid.set_walkable(0, y, False)
            self.grid.set_walkable(self.grid.width - 1, y, False)
        
        # Estructuras en el mapa
        structures = [
            # Casa 1 (arriba izquierda)
            [(5, 5), (6, 5), (7, 5), (8, 5), (9, 5),
             (5, 6), (9, 6),
             (5, 7), (9, 7),
             (5, 8), (9, 8),
             (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)],
            
            # Casa 2 (arriba derecha)
            [(25, 5), (26, 5), (27, 5), (28, 5),
             (25, 6), (28, 6),
             (25, 7), (28, 7),
             (25, 8), (26, 8), (27, 8), (28, 8)],
            
            # Barricadas centrales
            [(15, 12), (16, 12), (17, 12),
             (15, 13),
             (15, 14), (16, 14), (17, 14)],
            
            # Muros defensivos
            [(10, 18), (11, 18), (12, 18),
             (20, 18), (21, 18), (22, 18)],
            
            # Obstáculos adicionales
            [(7, 15), (8, 15),
             (7, 16), (8, 16)],
            
            [(24, 15), (25, 15),
             (24, 16), (25, 16)],
        ]
        
        for structure in structures:
            for x, y in structure:
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    self.grid.set_walkable(x, y, False)
    
    def create_test_enemies(self):
        """Crea una oleada inicial de enemigos variados"""
        enemy_types = [
            (EnemyType.SOLDIER, 3),
            (EnemyType.ELITE, 1),
            (EnemyType.SNIPER, 1),
        ]
        
        spawn_points = [
            (100, 100), (SCREEN_WIDTH - 100, 100),
            (100, SCREEN_HEIGHT - 100), (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
            (SCREEN_WIDTH // 2, 100), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        ]
        
        for enemy_type, count in enemy_types:
            for i in range(count):
                if spawn_points:
                    pos = random.choice(spawn_points)
                    spawn_points.remove(pos)
                    self.spawn_enemy(pos[0], pos[1], enemy_type)
    
    def spawn_enemy(self, x, y, enemy_type=EnemyType.SOLDIER):
        """Genera un enemigo en la posición especificada"""
        enemy = Enemy(x, y, enemy_type)
        enemy.player = self.player
        enemy.pathfinder = self.pathfinder
        enemy.game = self
        
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
        print(f"Spawned {enemy_type} en ({x}, {y})")
        
    def spawn_wave(self):
        """Genera una nueva oleada de enemigos"""
        self.wave += 1
        enemies_count = min(self.max_enemies_per_wave + self.wave, 15)
        
        # Tipos de enemigos según la oleada
        available_types = [EnemyType.SOLDIER]
        
        if self.wave >= 2:
            available_types.append(EnemyType.ELITE)
        if self.wave >= 3:
            available_types.append(EnemyType.KAMIKAZE)
        if self.wave >= 4:
            available_types.append(EnemyType.SNIPER)
        if self.wave >= 5:
            available_types.append(EnemyType.OFFICER)
        
        # Puntos de spawn en los bordes
        spawn_positions = []
        
        # Bordes superior e inferior
        for i in range(5):
            x = random.randint(100, SCREEN_WIDTH - 100)
            spawn_positions.append((x, 50))
            spawn_positions.append((x, SCREEN_HEIGHT - 50))
        
        # Bordes izquierdo y derecho
        for i in range(5):
            y = random.randint(100, SCREEN_HEIGHT - 100)
            spawn_positions.append((50, y))
            spawn_positions.append((SCREEN_WIDTH - 50, y))
        
        # Generar enemigos
        for i in range(enemies_count):
            if spawn_positions:
                pos = random.choice(spawn_positions)
                enemy_type = random.choice(available_types)
                
                # Mayor probabilidad de enemigos básicos
                if enemy_type != EnemyType.SOLDIER and random.random() < 0.6:
                    enemy_type = EnemyType.SOLDIER
                
                self.spawn_enemy(pos[0], pos[1], enemy_type)
                spawn_positions.remove(pos)
        
        print(f"¡Oleada {self.wave} iniciada con {enemies_count} enemigos!")
    
    def init_gamepad(self):
        """Inicializa el gamepad si está conectado"""
        pygame.joystick.init()
        self.gamepad = None
        
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad detectado: {self.gamepad.get_name()}")
        else:
            print("No se detectó gamepad. Usando teclado y mouse.")
    
    def init_audio(self):
        """Inicializa el sistema de audio"""
        pygame.mixer.init()
        
        # Reproducir música de batalla
        self.audio_manager.play_music("battle_theme")
    
    def create_tiled_floor(self):
        """Crea un suelo con tiles variados"""
        self.floor_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        tile_types = ['grass', 'dirt', 'grass', 'grass']  # Más grass que dirt
        
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            for x in range(0, SCREEN_WIDTH, TILE_SIZE):
                tile_type = random.choice(tile_types)
                tile = VisualEffects.create_tile_texture(TILE_SIZE, tile_type)
                self.floor_surface.blit(tile, (x, y))
    
    def create_enhanced_map(self):
        """Crea un mapa más interesante con diferentes tipos de obstáculos"""
        # Limpiar mapa
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.grid.set_walkable(x, y, True)
        
        # Bordes del mapa con muros
        for x in range(self.grid.width):
            self.grid.set_walkable(x, 0, False)
            self.grid.set_walkable(x, self.grid.height - 1, False)
        
        for y in range(self.grid.height):
            self.grid.set_walkable(0, y, False)
            self.grid.set_walkable(self.grid.width - 1, y, False)
        
        # Estructuras variadas
        self.create_building(5, 5, 5, 5, 'wall')
        self.create_building(25, 5, 4, 4, 'crate')
        self.create_building(15, 12, 3, 3, 'barrel')
        self.create_building(10, 18, 3, 5, 'wall')
        self.create_building(20, 18, 3, 5, 'wall')
        
        # Obstáculos individuales
        obstacles = [
            (7, 15, 'tree'), (8, 16, 'tree'),
            (24, 15, 'barrel'), (25, 16, 'barrel'),
            (15, 8, 'crate'), (16, 8, 'crate')
        ]
        
        for x, y, obstacle_type in obstacles:
            if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                self.grid.set_walkable(x, y, False)
    
    def create_building(self, start_x, start_y, width, height, wall_type):
        """Crea una estructura rectangular"""
        for y in range(start_y, min(start_y + height, self.grid.height)):
            for x in range(start_x, min(start_x + width, self.grid.width)):
                # Solo bordes para edificios, dejando el interior caminable
                if x == start_x or x == start_x + width - 1 or \
                   y == start_y or y == start_y + height - 1:
                    self.grid.set_walkable(x, y, False)
    
    def apply_progression_stats(self):
        """Aplica las estadísticas de progresión al jugador"""
        if hasattr(self.player, 'max_health'):
            self.player.max_health = self.progression.stats['max_health']
            self.player.health = self.player.max_health
            self.player.damage_boost = self.progression.stats['damage_multiplier']
            self.player.fire_rate_boost = self.progression.stats['fire_rate']
            self.player.speed = PLAYER_SPEED * self.progression.stats['movement_speed']
    
    def start_next_wave(self):
        """Inicia la siguiente oleada"""
        self.wave += 1
        wave_config = self.wave_manager.get_wave_config(self.wave)
        
        print(f"\n=== OLEADA {self.wave} ===")
        print(f"Enemigos: {wave_config['enemy_count']}")
        print(f"Modificadores: {wave_config['modifiers']}")
        
        # Preparar cola de spawn
        self.spawn_queue = []
        for enemy_type, probability in wave_config['enemy_types']:
            count = int(wave_config['enemy_count'] * probability)
            self.spawn_queue.extend([enemy_type] * count)
        
        random.shuffle(self.spawn_queue)
        self.enemies_remaining = len(self.spawn_queue)
        self.spawn_timer = 0
        
        # Aplicar modificadores de oleada
        self.apply_wave_modifiers(wave_config['modifiers'])
        
        # Efectos visuales de nueva oleada
        self.show_wave_announcement()
    
    def apply_wave_modifiers(self, modifiers):
        """Aplica modificadores especiales a la oleada"""
        for modifier in modifiers:
            if modifier == 'fog_of_war':
                # Activar niebla
                pass
            elif modifier == 'fast_enemies':
                # Los enemigos serán más rápidos
                pass
            # etc...
    
    def show_wave_announcement(self):
        """Muestra anuncio de nueva oleada"""
        # TODO: Implementar anuncio visual
        self.audio_manager.play_sound("wave_start", 0.7)
    
    def update(self, dt, events):
        """Actualiza la lógica del juego"""
        if self.state == GameState.PLAYING:
            # Obtener input
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            self.update_screen_shake(dt)
            # Manejar eventos específicos
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.show_pathfinding = not self.show_pathfinding
                    elif event.key == pygame.K_d:
                        self.show_debug_info = not self.show_debug_info
                    elif event.key == pygame.K_SPACE:
                        # Spawn manual de enemigo para pruebas
                        enemy_types = [EnemyType.SOLDIER, EnemyType.ELITE, 
                                     EnemyType.SNIPER, EnemyType.KAMIKAZE, 
                                     EnemyType.OFFICER]
                        self.spawn_enemy(
                            random.randint(100, SCREEN_WIDTH - 100),
                            random.randint(100, SCREEN_HEIGHT - 100),
                            random.choice(enemy_types)
                        )
            
            # Actualizar jugador con input
            self.player.handle_input(keys, mouse_pos, mouse_buttons, self.gamepad)
            
            # Actualizar todos los sprites
            self.all_sprites.update(dt)
            self.bullets.update(dt)
            self.explosions.update(dt)
            self.powerups.update(dt)
            
            # Actualizar sistemas
            self.particle_system.update(dt)
            
            # Actualizar screen shake
            if self.screen_shake > 0:
                self.screen_shake -= dt
            
            # Verificar colisiones
            self.check_collisions()
            
            # Procesar solicitudes de las entidades
            self.process_entity_requests()
            
            # Spawn de enemigos
            if len(self.enemies) == 0:
                self.spawn_timer += dt
                if self.spawn_timer >= self.spawn_cooldown:
                    self.spawn_wave()
                    self.spawn_timer = 0
            
            # Verificar condición de victoria/derrota
            if self.player.health <= 0:
                self.state = GameState.GAME_OVER
                print("¡GAME OVER!")
            
        elif self.state == GameState.MENU:
            # TODO: Implementar lógica del menú
            pass
    
    def process_entity_requests(self):
        """Procesa solicitudes de las entidades (balas, explosiones, etc.)"""
        # Procesar solicitudes de balas
        for enemy in self.enemies:
            if "bullet_request" in enemy.behavior_tree.blackboard:
                req = enemy.behavior_tree.blackboard["bullet_request"]
                self.create_bullet(
                    req["position"].x, req["position"].y,
                    req["angle"], req["damage"], owner=enemy
                )
                del enemy.behavior_tree.blackboard["bullet_request"]
            
            # Procesar solicitudes de explosiones
            if "explosion_request" in enemy.behavior_tree.blackboard:
                req = enemy.behavior_tree.blackboard["explosion_request"]
                self.create_explosion(
                    req["position"].x, req["position"].y,
                    req["radius"], req["damage"]
                )
                del enemy.behavior_tree.blackboard["explosion_request"]
            
            # Procesar solicitudes de power-ups
            if "powerup_request" in enemy.behavior_tree.blackboard:
                req = enemy.behavior_tree.blackboard["powerup_request"]
                self.create_powerup(
                    req["position"].x, req["position"].y,
                    req["type"]
                )
                del enemy.behavior_tree.blackboard["powerup_request"]
        
        # Procesar balas del jugador
        if hasattr(self.player, "shoot_request") and self.player.shoot_request:
            self.create_bullet(
                self.player.pos.x, self.player.pos.y,
                self.player.angle, BULLET_DAMAGE, owner=self.player
            )
            self.player.shoot_request = False
    
    def create_bullet(self, x, y, angle, damage=BULLET_DAMAGE, owner=None):
        """Crea una bala"""
        bullet = self.bullet_manager.create_bullet(x, y, angle, damage, owner=owner)
        self.all_sprites.add(bullet)
        
        # Efectos visuales
        muzzle_x = x + math.cos(angle) * 20
        muzzle_y = y + math.sin(angle) * 20
        self.particle_system.create_muzzle_flash(muzzle_x, muzzle_y, angle)
        
        # Sonido
        if owner == self.player:
            self.audio_manager.play_sound("player_shoot", 0.5)
        else:
            self.audio_manager.play_sound("enemy_shoot", 0.3)
        
    def create_explosion(self, x, y, radius=50, damage=50):
        """Crea una explosión"""
        explosion = self.bullet_manager.create_explosion(x, y, radius, damage)
        self.all_sprites.add(explosion)
        
        # Efectos
        self.particle_system.create_explosion(x, y, radius / 50)
        self.add_screen_shake(radius / 5, 0.3)
        
        # Sonido
        if radius > 75:
            self.audio_manager.play_explosion("big")
        else:
            self.audio_manager.play_explosion("small")
        
    def create_powerup(self, x, y, powerup_type):
        """Crea un power-up"""
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)
    
    def check_collisions(self):
        """Verifica todas las colisiones del juego"""
        # Balas vs Enemigos
        enemy_hits = self.bullet_manager.check_bullet_collisions(
            self.enemies, self.grid
        )
        
        for enemy, bullets in enemy_hits.items():
            for bullet in bullets:
                if bullet.owner != enemy:
                    enemy.take_damage(bullet.damage)
                    if enemy.health <= 0:
                        self.score += 100 * (self.wave + 1)
        
        # Balas vs Jugador
        player_hits = pygame.sprite.spritecollide(
            self.player, self.bullets, True
        )
        
        for bullet in player_hits:
            if bullet.owner != self.player:
                self.player.take_damage(bullet.damage)
        
        # Explosiones vs Todos
        all_targets = [self.player] + list(self.enemies)
        self.bullet_manager.check_explosion_damage(all_targets)
        
        # Jugador vs Power-ups
        powerup_hits = pygame.sprite.spritecollide(
            self.player, self.powerups, False
        )
        
        for powerup in powerup_hits:
            powerup.apply_to_player(self.player)
            self.score += 50
        
        # Enemigos vs Jugador (colisión directa)
        enemy_collisions = pygame.sprite.spritecollide(
            self.player, self.enemies, False
        )
        
        for enemy in enemy_collisions:
            if enemy.enemy_type == EnemyType.KAMIKAZE:
                # Kamikaze explota al tocar
                self.create_explosion(enemy.pos.x, enemy.pos.y, 100, 75)
                enemy.kill()
            else:
                # Daño por contacto
                self.player.take_damage(10)
                # Empujar al jugador
                direction = self.player.pos - enemy.pos
                if direction.length() > 0:
                    direction = direction.normalize()
                    self.player.pos += direction * 50
    
    def draw(self):
        """Dibuja todo en pantalla"""
        # Limpiar pantalla
        self.screen.fill(DARK_GREEN)
        
        # Aplicar screen shake
        shake_offset = [0, 0]
        if self.screen_shake > 0:
            shake_offset[0] = random.randint(-self.screen_shake_intensity, 
                                            self.screen_shake_intensity)
            shake_offset[1] = random.randint(-self.screen_shake_intensity, 
                                            self.screen_shake_intensity)
        
        # Crear superficie temporal si hay shake
        if self.screen_shake > 0:
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            temp_surface.fill(DARK_GREEN)
            draw_surface = temp_surface
        else:
            draw_surface = self.screen
        
        if self.state == GameState.PLAYING:
            # Dibujar grid (opcional)
            if self.show_pathfinding:
                self.draw_grid(draw_surface)
            
            # Dibujar obstáculos
            self.draw_obstacles(draw_surface)
            
            # Dibujar trails de balas
            self.bullet_manager.draw_trails(draw_surface)
            
            # Dibujar sprites (orden importante)
            for sprite in sorted(self.all_sprites, key=lambda s: s.rect.bottom):
                draw_surface.blit(sprite.image, sprite.rect)
            
            # Dibujar partículas
            self.particle_system.draw(draw_surface)
            
            # Dibujar debug de enemigos
            if self.show_debug_info:
                for enemy in self.enemies:
                    enemy.draw_debug(draw_surface)
            
            # Si hay shake, dibujar la superficie temporal con offset
            if self.screen_shake > 0:
                self.screen.blit(temp_surface, shake_offset)
            
            # Dibujar UI (siempre sin shake)
            self.draw_ui()
            
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
    
    def draw_grid(self, surface=None):
        """Dibuja el grid del pathfinding"""
        if surface is None:
            surface = self.screen
            
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(surface, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT), 1)
        
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, (50, 50, 50), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_obstacles(self, surface=None):
        """Dibuja los obstáculos del mapa"""
        if surface is None:
            surface = self.screen
            
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                node = self.grid.get_node(x, y)
                if node and not node.walkable:
                    rect = pygame.Rect(
                        x * TILE_SIZE, 
                        y * TILE_SIZE, 
                        TILE_SIZE, 
                        TILE_SIZE
                    )
                    pygame.draw.rect(surface, (80, 80, 80), rect)
                    pygame.draw.rect(surface, BLACK, rect, 2)
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Barra de vida
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 10
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (100, 0, 0), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Vida actual
        health_width = int((self.player.health / PLAYER_HEALTH) * bar_width)
        pygame.draw.rect(self.screen, RED, 
                        (bar_x, bar_y, health_width, bar_height))
        
        # Borde
        pygame.draw.rect(self.screen, WHITE, 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Texto de vida
        health_text = small_font.render(f"{self.player.health}/{PLAYER_HEALTH}", 
                                       True, WHITE)
        self.screen.blit(health_text, (bar_x + 5, bar_y + 2))
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 40))
        
        # Oleada
        wave_text = font.render(f"Oleada: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 80))
        
        # Enemigos restantes
        enemies_text = small_font.render(f"Enemigos: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemies_text, (10, 120))
        
        # Instrucciones
        if self.show_debug_info:
            instructions = [
                "WASD/Flechas - Mover",
                "Mouse - Apuntar",
                "Click/Gamepad RT - Disparar",
                "P - Toggle pathfinding",
                "D - Toggle debug",
                "Space - Spawn enemigo",
            ]
            
            y = SCREEN_HEIGHT - 180
            for text in instructions:
                surf = small_font.render(text, True, WHITE)
                self.screen.blit(surf, (10, y))
                y += 25
        
        # Mini radar
        self.draw_minimap()
    
    def draw_minimap(self):
        """Dibuja un mini mapa/radar"""
        minimap_size = 150
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = 10
        
        # Fondo
        pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                        (minimap_x, minimap_y, minimap_size, minimap_size))
        
        # Escala
        scale_x = minimap_size / SCREEN_WIDTH
        scale_y = minimap_size / SCREEN_HEIGHT
        
        # Jugador (centro del radar, verde)
        player_x = minimap_x + int(self.player.pos.x * scale_x)
        player_y = minimap_y + int(self.player.pos.y * scale_y)
        pygame.draw.circle(self.screen, GREEN, (player_x, player_y), 3)
        
        # Enemigos (puntos rojos)
        for enemy in self.enemies:
            enemy_x = minimap_x + int(enemy.pos.x * scale_x)
            enemy_y = minimap_y + int(enemy.pos.y * scale_y)
            
            # Color según tipo
            if enemy.enemy_type == EnemyType.KAMIKAZE:
                color = (255, 165, 0)  # Naranja
            elif enemy.enemy_type == EnemyType.OFFICER:
                color = (0, 255, 0)  # Verde
            else:
                color = RED
                
            pygame.draw.circle(self.screen, color, (enemy_x, enemy_y), 2)
        
        # Borde
        pygame.draw.rect(self.screen, WHITE, 
                        (minimap_x, minimap_y, minimap_size, minimap_size), 2)
    
    def draw_game_over(self):
        """Dibuja la pantalla de Game Over"""
        # Oscurecer pantalla
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto
        font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = small_font.render(f"Score Final: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        wave_text = small_font.render(f"Alcanzaste la oleada {self.wave}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(wave_text, wave_rect)
        
        restart_text = small_font.render("Presiona R para reiniciar", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        self.screen.blit(restart_text, restart_rect)