import pygame
import random
import math
import time
from scripts.player import Player
from scripts.enemy import Enemy
from scripts.bullet import Bullet, BulletManager, PowerUp
from scripts.utils.constants import *
from scripts.ai.pathfinding import Grid, AStar
from scripts.utils.particle_system import ParticleSystem
from scripts.utils.audio_manager import get_audio_manager

class Game:
    """Clase principal del juego con A* y Árbol de Comportamiento"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Referencias de juego
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.game = self
        
        # Grupos de sprites
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Sistemas de juego
        self.bullet_manager = BulletManager(self.bullets, self.explosions)
        self.particle_system = ParticleSystem()
        self.audio_manager = get_audio_manager()
        
        # Sistema de pathfinding A*
        self.setup_pathfinding()
        
        # Estado del juego
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.enemies_to_spawn = 5
        self.spawn_timer = 0
        self.spawn_delay = 2.0
        
        # Control
        self.gamepad = None
        self.init_gamepad()
        
        # Debug
        self.show_debug_info = False
        self.show_pathfinding = False
        
        # Efectos visuales
        self.screen_shake_amount = 5
        self.screen_shake_duration = 5
        
        # Generar enemigos iniciales
        self.spawn_initial_enemies()
        
    def setup_pathfinding(self):
        """Configura el sistema de pathfinding A*"""
        # Crear grid basado en el tamaño de la pantalla
        grid_width = SCREEN_WIDTH // TILE_SIZE
        grid_height = SCREEN_HEIGHT // TILE_SIZE
        
        self.grid = Grid(grid_width, grid_height, TILE_SIZE)
        self.pathfinder = AStar(self.grid)
        
        # Crear algunos obstáculos básicos para demostrar A*
        self.create_obstacles()
        
        print(f"✓ Pathfinding A* inicializado: {grid_width}x{grid_height} grid")
        
    def create_obstacles(self):
        """Crea obstáculos en el mapa para demostrar A*"""
        # Paredes verticales
        for y in range(5, 15):
            self.grid.set_walkable(10, y, False)
            self.grid.set_walkable(20, y, False)
        
        # Paredes horizontales
        for x in range(10, 20):
            self.grid.set_walkable(x, 8, False)
            self.grid.set_walkable(x, 18, False)
        
        # Obstáculos adicionales esparcidos
        obstacles = [
            (5, 5), (6, 5), (7, 5),
            (25, 10), (26, 10), (27, 10),
            (15, 20), (16, 20), (17, 20),
            (30, 5), (31, 5), (32, 5)
        ]
        
        for x, y in obstacles:
            self.grid.set_walkable(x, y, False)
            
        print(f"✓ Obstáculos creados para demostrar A*")
    
    def init_gamepad(self):
        """Inicializa el gamepad"""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"✓ Gamepad detectado: {self.gamepad.get_name()}")
    
    def spawn_initial_enemies(self):
        """Genera enemigos iniciales"""
        for i in range(10):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            
            # Asegurar que no spawn en obstáculos
            while not self.is_position_walkable(x, y):
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
            
            enemy_type = random.choice([EnemyType.SOLDIER, EnemyType.ELITE, EnemyType.KAMIKAZE])
            self.spawn_enemy(x, y, enemy_type)
    
    def spawn_enemy(self, x, y, enemy_type):
        """Crea un nuevo enemigo con IA"""
        enemy = Enemy(x, y, enemy_type)
        
        # Configurar referencias para la IA
        enemy.player = self.player
        enemy.pathfinder = self.pathfinder
        enemy.game = self
        
        self.enemies.add(enemy)
        print(f"✓ {enemy_type} spawneado en ({x}, {y})")
    
    def is_position_walkable(self, x, y):
        """Verifica si una posición es caminable"""
        node = self.grid.get_node_from_world_pos(x, y)
        return node and node.walkable
    
    def update(self, dt, events):
        """Actualiza la lógica del juego"""
        # Manejar input
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Actualizar jugador
        self.player.handle_input(keys, mouse_pos, mouse_buttons, self.gamepad)
        self.player.update(dt)
        
        # Procesar disparo del jugador
        if self.player.shoot_request:
            self.player.shoot_request = False
            bullet = self.bullet_manager.create_bullet(
                self.player.pos.x, self.player.pos.y,
                self.player.angle, self.player.get_damage(),
                BULLET_SPEED, self.player
            )
            
            # Efectos de disparo
            self.particle_system.create_muzzle_flash(
                self.player.pos.x, self.player.pos.y, self.player.angle
            )
            self.audio_manager.play_sound("player_shoot", 0.6)
        
        # Actualizar enemigos (usan A* y comportamiento)
        for enemy in self.enemies:
            enemy.update(dt)
            
            # Procesar solicitudes de disparo de enemigos
            if hasattr(enemy.behavior_tree, 'blackboard'):
                bb = enemy.behavior_tree.blackboard
                
                # Solicitud de bala
                if "bullet_request" in bb:
                    req = bb["bullet_request"]
                    self.bullet_manager.create_bullet(
                        req["position"].x, req["position"].y,
                        req["angle"], req["damage"], 
                        BULLET_SPEED * 0.8, req["owner"]
                    )
                    del bb["bullet_request"]
                    
                    # Efectos
                    self.particle_system.create_muzzle_flash(
                        req["position"].x, req["position"].y, req["angle"]
                    )
                    self.audio_manager.play_sound("enemy_shoot", 0.4)
                
                # Solicitud de explosión
                if "explosion_request" in bb:
                    req = bb["explosion_request"]
                    self.create_explosion(req["position"].x, req["position"].y,
                                        req["radius"], req["damage"])
                    del bb["explosion_request"]
                
                # Solicitud de power-up
                if "powerup_request" in bb:
                    req = bb["powerup_request"]
                    powerup = PowerUp(req["position"].x, req["position"].y, req["type"])
                    self.powerups.add(powerup)
                    del bb["powerup_request"]
        
        # Actualizar proyectiles
        self.bullets.update(dt)
        self.explosions.update(dt)
        
        # Verificar colisiones
        self.check_collisions()
        
        # Actualizar power-ups
        self.powerups.update(dt)
        
        # Verificar colisiones con power-ups
        for powerup in self.powerups:
            if powerup.rect.colliderect(self.player.rect):
                powerup.apply_to_player(self.player)
        
        # Actualizar sistemas
        self.particle_system.update(dt)
        
        # Spawn de enemigos
        self.update_enemy_spawning(dt)
        
        # Screen shake
        self.update_screen_shake(dt)
        
        # Verificar estado del juego
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
        elif len(self.enemies) == 0 and self.enemies_to_spawn <= 0:
            self.next_wave()
    
    def create_explosion(self, x, y, radius, damage):
        """Crea una explosión"""
        from scripts.bullet import Explosion
        explosion = Explosion(x, y, radius, damage)
        self.explosions.add(explosion)
        
        # Efectos adicionales
        self.particle_system.create_explosion(x, y, 1.5)
        self.audio_manager.play_explosion("big" if radius > 60 else "small")
        self.add_screen_shake(radius / 5, 0.3)
    
    def check_collisions(self):
        """Verifica todas las colisiones"""
        # Balas vs objetivos
        bullet_hits = self.bullet_manager.check_bullet_collisions(
            list(self.enemies) + [self.player], self.grid
        )
        
        # Procesar hits
        for target, bullets in bullet_hits.items():
            total_damage = sum(bullet.damage for bullet in bullets)
            target.take_damage(total_damage)
            
            # Efectos de impacto
            for bullet in bullets:
                self.particle_system.create_blood_splatter(
                    target.pos.x, target.pos.y, bullet.angle + math.pi
                )
        
        # Explosiones vs objetivos
        self.bullet_manager.check_explosion_damage(
            list(self.enemies) + [self.player]
        )
    
    def update_enemy_spawning(self, dt):
        """Actualiza el spawn de enemigos"""
        if self.enemies_to_spawn > 0:
            self.spawn_timer += dt
            
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                
                # Encontrar posición válida
                for attempts in range(10):
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    
                    # Verificar distancia del jugador
                    if math.hypot(x - self.player.pos.x, y - self.player.pos.y) > 200:
                        if self.is_position_walkable(x, y):
                            enemy_type = random.choice([
                                EnemyType.SOLDIER, EnemyType.ELITE, 
                                EnemyType.KAMIKAZE, EnemyType.SNIPER
                            ])
                            self.spawn_enemy(x, y, enemy_type)
                            self.enemies_to_spawn -= 1
                            break
    
    def next_wave(self):
        """Avanza a la siguiente oleada"""
        self.wave += 1
        self.enemies_to_spawn = 3 + self.wave * 2
        self.spawn_delay = max(0.5, 2.0 - self.wave * 0.1)
        
        print(f"🌊 OLEADA {self.wave} - {self.enemies_to_spawn} enemigos")
        
        # Curar parcialmente al jugador
        heal_amount = min(25, self.player.max_health - self.player.health)
        self.player.heal(heal_amount)
    
    def add_screen_shake(self, amount, duration):
        """Añade screen shake"""
        self.screen_shake_amount = max(self.screen_shake_amount, amount)
        self.screen_shake_duration = max(self.screen_shake_duration, duration)
    
    def update_screen_shake(self, dt):
        """Actualiza el screen shake"""
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            if self.screen_shake_duration <= 0:
                self.screen_shake_amount = 0
    
    def draw(self):
        """Dibuja todo el juego"""
        # Limpiar pantalla
        self.screen.fill((40, 60, 40))  # Verde militar
        
        # Aplicar screen shake
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake_amount > 0:
            shake_offset_x = random.randint(-self.screen_shake_amount, self.screen_shake_amount)
            shake_offset_y = random.randint(-self.screen_shake_amount, self.screen_shake_amount)
        
        # Crear superficie temporal para shake
        if self.screen_shake_amount > 0:
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            temp_surface.fill((40, 60, 40))
            draw_surface = temp_surface
        else:
            draw_surface = self.screen
        
        # Dibujar obstáculos
        self.draw_obstacles(draw_surface)
        
        # Dibujar trails de balas
        self.bullet_manager.draw_trails(draw_surface)
        
        # Dibujar sprites
        draw_surface.blit(self.player.image, self.player.rect)
        self.enemies.draw(draw_surface)
        self.bullets.draw(draw_surface)
        self.explosions.draw(draw_surface)
        self.powerups.draw(draw_surface)
        
        # Dibujar efectos de partículas
        self.particle_system.draw(draw_surface)
        
        # Debug del pathfinding
        if self.show_pathfinding:
            self.draw_pathfinding_debug(draw_surface)
        
        # Debug de enemigos
        if self.show_debug_info:
            for enemy in self.enemies:
                enemy.draw_debug(draw_surface)
        
        # Aplicar screen shake
        if self.screen_shake_amount > 0:
            self.screen.blit(temp_surface, (shake_offset_x, shake_offset_y))
        
        # UI
        self.draw_ui()
    
    def draw_obstacles(self, surface):
        """Dibuja los obstáculos del mapa"""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                node = self.grid.get_node(x, y)
                if node and not node.walkable:
                    rect = pygame.Rect(
                        x * TILE_SIZE, y * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    pygame.draw.rect(surface, (100, 50, 50), rect)
                    pygame.draw.rect(surface, (80, 40, 40), rect, 2)
    
    def draw_pathfinding_debug(self, surface):
        """Dibuja información de debug del pathfinding"""
        # Dibujar grid
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(surface, (60, 60, 60), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, (60, 60, 60), (0, y), (SCREEN_WIDTH, y), 1)
        
        # Dibujar paths de enemigos
        for enemy in self.enemies:
            if enemy.path:
                self.pathfinder.draw_path(surface, enemy.path, (255, 255, 0))
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Vida del jugador
        health_bar_width = 200
        health_bar_height = 20
        health_x = 20
        health_y = 20
        
        # Fondo de la barra
        health_bg = pygame.Rect(health_x, health_y, health_bar_width, health_bar_height)
        pygame.draw.rect(self.screen, (100, 0, 0), health_bg)
        
        # Barra de vida actual
        health_percent = self.player.health / self.player.max_health
        health_width = int(health_bar_width * health_percent)
        if health_width > 0:
            health_rect = pygame.Rect(health_x, health_y, health_width, health_bar_height)
            pygame.draw.rect(self.screen, (0, 255, 0), health_rect)
        
        # Borde
        pygame.draw.rect(self.screen, WHITE, health_bg, 2)
        
        # Texto de vida
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"Vida: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (health_x, health_y + 25))
        
        # Score y oleada
        score_text = font.render(f"Puntuación: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 70))
        
        wave_text = font.render(f"Oleada: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (20, 95))
        
        # Enemigos restantes
        enemies_left = len(self.enemies) + self.enemies_to_spawn
        enemies_text = font.render(f"Enemigos: {enemies_left}", True, WHITE)
        self.screen.blit(enemies_text, (20, 120))
        
        # Debug info
        if self.show_debug_info:
            debug_texts = [
                f"FPS: {pygame.time.Clock().get_fps():.0f}",
                f"Enemigos activos: {len(self.enemies)}",
                f"Balas activas: {len(self.bullets)}",
                f"Partículas: {len(self.particle_system.particles)}",
                f"Pathfinding: A* activo",
                f"Comportamiento: Árboles activos"
            ]
            
            small_font = pygame.font.Font(None, 20)
            for i, text in enumerate(debug_texts):
                debug_surface = small_font.render(text, True, YELLOW)
                self.screen.blit(debug_surface, (SCREEN_WIDTH - 250, 20 + i * 22))
        
        # Controles
        controls_font = pygame.font.Font(None, 18)
        controls = [
            "WASD/Flechas: Mover",
            "Mouse: Apuntar y disparar",
            
        ]
        
        for i, control in enumerate(controls):
            control_surface = controls_font.render(control, True, WHITE)
            self.screen.blit(control_surface, (20, SCREEN_HEIGHT - 100 + i * 20))
    
    def handle_events(self, events):
        """Maneja eventos específicos del juego"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.show_debug_info = not self.show_debug_info
                elif event.key == pygame.K_F2:
                    self.show_pathfinding = not self.show_pathfinding