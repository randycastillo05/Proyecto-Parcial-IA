import pygame
import sys
import math
import random
import json
import os
from enum import Enum

# ========================
# CONFIGURACIÓN DEL JUEGO
# ========================
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
FPS = 60

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
        surface.fill(color_fallback or Colors.WHITE)
        return surface
    return None

# ========================
# COLORES
# ========================
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (128, 128, 128)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class SoundManager:
    """Gestor de sonidos y música del juego"""
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.effects_volume = 0.7
        self.load_all_sounds()
        
    def load_all_sounds(self):
        """Carga todos los sonidos del juego"""
        # Directorio de sonidos
        sound_dir = "assets/sounds"
        music_dir = "assets/music"
        
        # Crear directorios si no existen
        os.makedirs(sound_dir, exist_ok=True)
        os.makedirs(music_dir, exist_ok=True)
        
        # Cargar efectos de sonido
        sound_files = {
            'shoot': ['shoot.wav', 'shoot.ogg', 'shoot.mp3'],
            'hit': ['hit.wav', 'hit.ogg', 'hit.mp3'],
            'explosion': ['explosion.wav', 'explosion.ogg', 'explosion.mp3'],
            'powerup': ['powerup.wav', 'powerup.ogg', 'powerup.mp3'],
            'game_over': ['game_over.wav', 'game_over.ogg', 'game_over.mp3'],
            'wave_complete': ['wave_complete.wav', 'wave_complete.ogg', 'wave_complete.mp3'],
            'hurt': ['hurt.wav', 'hurt.ogg', 'hurt.mp3']
        }
        
        for sound_name, filenames in sound_files.items():
            for filename in filenames:
                filepath = os.path.join(sound_dir, filename)
                if os.path.exists(filepath):
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                        self.sounds[sound_name].set_volume(self.effects_volume)
                        print(f"Sonido cargado: {sound_name} ({filename})")
                        break
                    except:
                        continue
                        
        # Buscar música
        self.menu_music = None
        self.game_music = None
        self.boss_music = None
        
        music_formats = ['.mp3', '.ogg', '.wav']
        
        # Música del menú
        for fmt in music_formats:
            menu_path = os.path.join(music_dir, f"menu{fmt}")
            if os.path.exists(menu_path):
                self.menu_music = menu_path
                print(f"Música de menú encontrada: menu{fmt}")
                break
                
        # Música del juego
        for fmt in music_formats:
            game_path = os.path.join(music_dir, f"game{fmt}")
            if os.path.exists(game_path):
                self.game_music = game_path
                print(f"Música de juego encontrada: game{fmt}")
                break
                
        # Música de jefe (opcional)
        for fmt in music_formats:
            boss_path = os.path.join(music_dir, f"boss{fmt}")
            if os.path.exists(boss_path):
                self.boss_music = boss_path
                print(f"Música de jefe encontrada: boss{fmt}")
                break
                
        # Si no hay música específica, buscar background
        if not self.menu_music or not self.game_music:
            for fmt in music_formats:
                bg_path = os.path.join(music_dir, f"background{fmt}")
                if os.path.exists(bg_path):
                    if not self.menu_music:
                        self.menu_music = bg_path
                    if not self.game_music:
                        self.game_music = bg_path
                    print(f"Usando música de fondo general: background{fmt}")
                    break
                    
    def play_sound(self, sound_name):
        """Reproduce un efecto de sonido"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_menu_music(self):
        """Reproduce la música del menú"""
        if self.menu_music:
            try:
                pygame.mixer.music.load(self.menu_music)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop infinito
            except:
                print("No se pudo reproducir la música del menú")
                
    def play_game_music(self):
        """Reproduce la música del juego"""
        if self.game_music:
            try:
                pygame.mixer.music.load(self.game_music)
                pygame.mixer.music.set_volume(self.music_volume * 0.7)  # Más bajo durante el juego
                pygame.mixer.music.play(-1)
            except:
                print("No se pudo reproducir la música del juego")
                
    def play_boss_music(self):
        """Reproduce la música del jefe"""
        if self.boss_music:
            try:
                pygame.mixer.music.load(self.boss_music)
                pygame.mixer.music.set_volume(self.music_volume * 0.9)
                pygame.mixer.music.play(-1)
            except:
                print("No se pudo reproducir la música del jefe")
                
    def stop_music(self):
        """Detiene la música"""
        pygame.mixer.music.stop()
        
    def pause_music(self):
        """Pausa la música"""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Reanuda la música"""
        pygame.mixer.music.unpause()
        
    def set_music_volume(self, volume):
        """Ajusta el volumen de la música (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def set_effects_volume(self, volume):
        """Ajusta el volumen de los efectos (0.0 a 1.0)"""
        self.effects_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.effects_volume)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, speed=8, color=Colors.YELLOW, is_enemy=False):
        super().__init__()
        
        # Intentar cargar sprite de bala
        if is_enemy:
            self.image = load_sprite("assets/images/enemy_bullet.png", (8, 8), color)
        else:
            self.image = load_sprite("assets/images/bullet.png", (8, 16), color)
            # Rotar la bala según la dirección
            if direction_x != 0 or direction_y != 0:
                angle = math.atan2(-direction_y, direction_x) * 180 / math.pi - 90
                self.image = pygame.transform.rotate(self.image, angle)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.is_enemy = is_enemy
        
    def update(self):
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        
        # Eliminar si sale de pantalla
        if (self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or 
            self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT):
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Cargar sprites del jugador
        self.sprites = {
            'up': load_sprite("assets/images/player_up.png", (32, 32), Colors.CYAN),
            'down': load_sprite("assets/images/player_down.png", (32, 32), Colors.CYAN),
            'left': load_sprite("assets/images/player_left.png", (32, 32), Colors.CYAN),
            'right': load_sprite("assets/images/player_right.png", (32, 32), Colors.CYAN)
        }
        
        # Si no hay sprites direccionales, intentar cargar uno general
        if not os.path.exists("assets/images/player_up.png"):
            default_sprite = load_sprite("assets/images/player.png", (32, 32), Colors.CYAN)
            self.sprites = {
                'up': default_sprite,
                'down': default_sprite,
                'left': default_sprite,
                'right': default_sprite
            }
        
        # Sprite inicial
        self.image = self.sprites['up']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.power_level = 1
        self.facing_direction = (0, -1)  # Mirando hacia arriba por defecto
        self.current_sprite = 'up'
        
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Mantener dentro de pantalla
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            # Normalizar el vector de movimiento
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
                
                # Actualizar dirección de mirada y sprite
                self.facing_direction = (dx, dy)
                
                # Cambiar sprite según dirección
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self.current_sprite = 'right'
                    else:
                        self.current_sprite = 'left'
                else:
                    if dy > 0:
                        self.current_sprite = 'down'
                    else:
                        self.current_sprite = 'up'
                
                self.image = self.sprites[self.current_sprite]
        
        # Aplicar movimiento
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
    def shoot(self, direction_x=None, direction_y=None):
        if self.shoot_cooldown <= 0:
            # Si no se especifica dirección, usar la dirección de mirada
            if direction_x is None or direction_y is None:
                direction_x, direction_y = self.facing_direction
            
            bullet = Bullet(self.rect.centerx, self.rect.centery, 
                          direction_x, direction_y, speed=10, color=Colors.YELLOW)
            self.shoot_cooldown = 10
            return bullet
        return None
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__()
        self.enemy_type = enemy_type
        
        # Configurar según tipo
        if enemy_type == "basic":
            self.image = load_sprite("assets/images/enemy.png", (24, 24), Colors.RED)
            self.health = 30
            self.speed = 2
            self.points = 100
        elif enemy_type == "fast":
            self.image = load_sprite("assets/images/enemy_fast.png", (20, 20), Colors.ORANGE)
            self.health = 15
            self.speed = 4
            self.points = 150
        elif enemy_type == "heavy":
            self.image = load_sprite("assets/images/enemy_heavy.png", (36, 36), Colors.PURPLE)
            self.health = 80
            self.speed = 1
            self.points = 300
        elif enemy_type == "shooter":
            self.image = load_sprite("assets/images/enemy_shooter.png", (28, 28), Colors.YELLOW)
            self.health = 40
            self.speed = 1.5
            self.points = 200
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_health = self.health
        self.shoot_cooldown = 0
        self.ai_timer = 0
        
    def update(self, player):
        self.ai_timer += 1
        
        # Movimiento hacia el jugador
        if player:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalizar dirección
                dx /= distance
                dy /= distance
                
                # Movimiento especial por tipo
                if self.enemy_type == "fast":
                    dx += math.sin(self.ai_timer * 0.1) * 0.3
                elif self.enemy_type == "shooter":
                    # Mantener distancia
                    if distance < 200:
                        dx *= -0.5
                        dy *= -0.5
                
                # Aplicar movimiento
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
                
        # Mantener dentro de pantalla
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Cooldown de disparo
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def draw_health_bar(self, screen):
        """Dibujar barra de vida si está dañado"""
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 8
            
            # Fondo de la barra
            pygame.draw.rect(screen, Colors.RED, (bar_x, bar_y, bar_width, bar_height))
            # Vida actual
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, Colors.GREEN, (bar_x, bar_y, health_width, bar_height))
            
    def shoot_at_player(self, player):
        if self.enemy_type in ["shooter"] and self.shoot_cooldown <= 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0 and distance < 300:
                dx /= distance
                dy /= distance
                
                bullet = Bullet(self.rect.centerx, self.rect.centery,
                              dx, dy, speed=5, color=Colors.RED, is_enemy=True)
                self.shoot_cooldown = 60
                return bullet
        return None
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        
        # Cargar sprites de powerups
        colors = {
            'health': Colors.GREEN,
            'power': Colors.YELLOW,
            'speed': Colors.BLUE,
            'multi': Colors.PURPLE
        }
        
        sprite_names = {
            'health': 'powerup_health.png',
            'power': 'powerup_power.png',
            'speed': 'powerup_speed.png',
            'multi': 'powerup_multi.png'
        }
        
        sprite_path = f"assets/images/{sprite_names.get(power_type, 'powerup.png')}"
        self.image = load_sprite(sprite_path, (16, 16), colors.get(power_type, Colors.WHITE))
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 300
        self.bounce_timer = 0
        
    def update(self):
        self.lifetime -= 1
        self.bounce_timer += 0.2
        
        # Efecto de rebote
        self.rect.y += math.sin(self.bounce_timer) * 0.5
        
        if self.lifetime <= 0:
            self.kill()

class AkariWarrior:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("⚔️ AKARI WARRIOR ⚔️")
        self.clock = pygame.time.Clock()
        
        # Sistema de sonido
        self.sound_manager = SoundManager()
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Estado del juego
        self.state = GameState.MENU
        self.running = True
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Estadísticas
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.high_score = self.load_high_score()
        
        # Control
        self.player = None
        self.wave_timer = 0
        self.enemies_spawned = 0
        
        # Direcciones de disparo
        self.shoot_direction = [0, -1]  # Por defecto hacia arriba
        
        # Inicializar Joystick/Gamepad
        pygame.joystick.init()
        self.joystick = None
        self.joystick_name = "No detectado"
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_name = self.joystick.get_name()
            print(f"Gamepad detectado: {self.joystick_name}")
            print(f"Ejes: {self.joystick.get_numaxes()}")
            print(f"Botones: {self.joystick.get_numbuttons()}")
        else:
            print("No se detectó ningún gamepad")
        
        # Configuración del joystick
        self.joystick_deadzone = 0.3
        self.last_shot_direction = [0, -1]
        
        # Iniciar música del menú
        self.sound_manager.play_menu_music()
        
    def load_high_score(self):
        try:
            with open("akari_warrior_high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open("akari_warrior_high_score.txt", "w") as f:
                    f.write(str(self.high_score))
            except:
                pass
                
    def start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.enemies_spawned = 0
        self.wave_timer = 0
        
        # Cambiar música
        self.sound_manager.play_game_music()
        
        # Limpiar grupos
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.powerups.empty()
        
        # Crear jugador
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.all_sprites.add(self.player)
        
        # Crear primera wave
        self.spawn_wave()
        
    def spawn_wave(self):
        wave_size = min(5 + self.wave, 15)
        enemy_types = ['basic']
        
        if self.wave >= 2:
            enemy_types.append('fast')
        if self.wave >= 3:
            enemy_types.append('heavy')
        if self.wave >= 4:
            enemy_types.append('shooter')
            
        # Música de jefe en waves especiales
        if self.wave % 5 == 0:
            self.sound_manager.play_boss_music()
            
        for _ in range(wave_size):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, 200)
            enemy_type = random.choice(enemy_types)
            
            enemy = Enemy(x, y, enemy_type)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            
        self.enemies_spawned = wave_size
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.MENU:
            # Teclado
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.start_game()
            
            # Gamepad
            if self.joystick:
                # Botón A (Xbox) / X (PlayStation) - típicamente botón 0
                if self.joystick.get_button(0):
                    self.start_game()
                
        elif self.state == GameState.PLAYING:
            # Pausa
            if keys[pygame.K_ESCAPE]:
                self.state = GameState.PAUSED
                self.sound_manager.pause_music()
                
            if self.joystick and self.joystick.get_button(7):  # Start button
                self.state = GameState.PAUSED
                self.sound_manager.pause_music()
                
            if self.player:
                # === MOVIMIENTO ===
                dx, dy = 0, 0
                
                # Teclado
                if keys[pygame.K_a]:
                    dx = -1
                if keys[pygame.K_d]:
                    dx = 1
                if keys[pygame.K_w]:
                    dy = -1
                if keys[pygame.K_s]:
                    dy = 1
                
                # Gamepad - Stick izquierdo para movimiento
                if self.joystick:
                    # Eje 0 = horizontal, Eje 1 = vertical
                    joy_x = self.joystick.get_axis(0)
                    joy_y = self.joystick.get_axis(1)
                    
                    # Aplicar zona muerta
                    if abs(joy_x) > self.joystick_deadzone:
                        dx = joy_x
                    if abs(joy_y) > self.joystick_deadzone:
                        dy = joy_y
                    
                    # D-Pad como alternativa (si existe)
                    if self.joystick.get_numhats() > 0:
                        hat = self.joystick.get_hat(0)
                        if hat[0] != 0:  # Horizontal
                            dx = hat[0]
                        if hat[1] != 0:  # Vertical
                            dy = -hat[1]  # Invertir porque el hat Y está al revés
                
                # Aplicar movimiento
                if dx != 0 or dy != 0:
                    self.player.move(dx, dy)
                
                # === DISPARO ===
                shoot_dx, shoot_dy = 0, 0
                shot_fired = False
                
                # Teclado - Disparo direccional
                if keys[pygame.K_UP] or keys[pygame.K_i]:
                    shoot_dx, shoot_dy = 0, -1
                    shot_fired = True
                elif keys[pygame.K_DOWN] or keys[pygame.K_k]:
                    shoot_dx, shoot_dy = 0, 1
                    shot_fired = True
                elif keys[pygame.K_LEFT] or keys[pygame.K_j]:
                    shoot_dx, shoot_dy = -1, 0
                    shot_fired = True
                elif keys[pygame.K_RIGHT] or keys[pygame.K_l]:
                    shoot_dx, shoot_dy = 1, 0
                    shot_fired = True
                elif keys[pygame.K_SPACE]:
                    shoot_dx, shoot_dy = 0, -1  # Por defecto hacia arriba
                    shot_fired = True
                
                # Gamepad - Disparo
                if self.joystick:
                    # Opción 1: Stick derecho para dirección de disparo
                    if self.joystick.get_numaxes() >= 4:
                        right_x = self.joystick.get_axis(2)  # Eje 2 o 3 según el gamepad
                        right_y = self.joystick.get_axis(3)  # Eje 3 o 4 según el gamepad
                        
                        # Si el stick derecho está siendo usado
                        if abs(right_x) > self.joystick_deadzone or abs(right_y) > self.joystick_deadzone:
                            # Normalizar dirección
                            length = math.sqrt(right_x*right_x + right_y*right_y)
                            if length > 0:
                                shoot_dx = right_x / length
                                shoot_dy = right_y / length
                                shot_fired = True
                                self.last_shot_direction = [shoot_dx, shoot_dy]
                    
                    # Opción 2: Botones para disparar
                    # A/X para disparar en la última dirección
                    if self.joystick.get_button(0):
                        shoot_dx, shoot_dy = self.last_shot_direction
                        shot_fired = True
                    
                    # Botones de cara para direcciones específicas
                    if self.joystick.get_numbuttons() >= 4:
                        if self.joystick.get_button(3):  # Y/Triangle - Arriba
                            shoot_dx, shoot_dy = 0, -1
                            shot_fired = True
                        elif self.joystick.get_button(0):  # A/X - Abajo
                            shoot_dx, shoot_dy = 0, 1
                            shot_fired = True
                        elif self.joystick.get_button(2):  # X/Square - Izquierda
                            shoot_dx, shoot_dy = -1, 0
                            shot_fired = True
                        elif self.joystick.get_button(1):  # B/Circle - Derecha
                            shoot_dx, shoot_dy = 1, 0
                            shot_fired = True
                    
                    # Gatillos para disparo rápido
                    if self.joystick.get_numaxes() >= 5:
                        # RT/R2 para disparar
                        trigger = self.joystick.get_axis(4)  # O axis 5 según el gamepad
                        if trigger > 0.5:
                            shoot_dx, shoot_dy = self.last_shot_direction
                            shot_fired = True
                
                # Ejecutar disparo
                if shot_fired:
                    bullet = self.player.shoot(shoot_dx, shoot_dy)
                    if bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                        self.sound_manager.play_sound('shoot')
                        
        elif self.state == GameState.PAUSED:
            # Teclado
            if keys[pygame.K_ESCAPE] or keys[pygame.K_SPACE]:
                self.state = GameState.PLAYING
                self.sound_manager.unpause_music()
            
            # Gamepad
            if self.joystick:
                if self.joystick.get_button(7) or self.joystick.get_button(0):  # Start o A
                    self.state = GameState.PLAYING
                    self.sound_manager.unpause_music()
                
        elif self.state == GameState.GAME_OVER:
            # Teclado
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.state = GameState.MENU
                self.sound_manager.play_menu_music()
            
            # Gamepad
            if self.joystick:
                if self.joystick.get_button(0):  # A/X
                    self.state = GameState.MENU
                    self.sound_manager.play_menu_music()
                
    def update(self):
        if self.state != GameState.PLAYING:
            return
            
        # Actualizar jugador y balas
        if self.player:
            self.player.update()
        self.bullets.update()
        self.enemy_bullets.update()
        self.powerups.update()
        
        # Actualizar enemigos con referencia al jugador
        for enemy in self.enemies:
            enemy.update(self.player)
            
            # Enemigos disparan
            bullet = enemy.shoot_at_player(self.player)
            if bullet:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)
                
        # Colisiones: balas del jugador con enemigos
        for bullet in self.bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hit_enemies:
                bullet.kill()
                if enemy.take_damage(25):  # Daño por bala
                    self.score += enemy.points
                    enemy.kill()
                    self.sound_manager.play_sound('explosion')
                    
                    # Posible powerup
                    if random.random() < 0.3:
                        powerup_type = random.choice(['health', 'power', 'speed'])
                        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)
                else:
                    self.sound_manager.play_sound('hit')
                break
                
        # Colisiones: balas enemigas con jugador
        if self.player:
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_bullets:
                self.sound_manager.play_sound('hurt')
                if self.player.take_damage(20):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                        self.save_high_score()
                        self.sound_manager.play_sound('game_over')
                        self.sound_manager.stop_music()
                    else:
                        # Resetear jugador
                        self.player.health = self.player.max_health
                        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
                        
            # Colisiones: enemigos con jugador
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hit_enemies:
                self.sound_manager.play_sound('hurt')
                if self.player.take_damage(30):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                        self.save_high_score()
                        self.sound_manager.play_sound('game_over')
                        self.sound_manager.stop_music()
                    else:
                        self.player.health = self.player.max_health
                        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
                        
            # Colisiones: powerups con jugador
            hit_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in hit_powerups:
                self.sound_manager.play_sound('powerup')
                if powerup.power_type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.power_type == 'power':
                    self.player.power_level += 1
                elif powerup.power_type == 'speed':
                    self.player.speed = min(8, self.player.speed + 0.5)
                    
        # Verificar nueva wave
        if len(self.enemies) == 0:
            self.wave += 1
            self.score += 500
            self.sound_manager.play_sound('wave_complete')
            
            # Volver a música normal después de wave de jefe
            if (self.wave - 1) % 5 == 0 and self.wave > 1:
                self.sound_manager.play_game_music()
                
            pygame.time.wait(1000)  # Pausa entre waves
            self.spawn_wave()
            
    def draw_hud(self):
        # Fondo del HUD
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(self.screen, Colors.WHITE, (0, 0, SCREEN_WIDTH, 80), 2)
        
        # Textos del HUD
        score_text = self.font.render(f"PUNTOS: {self.score}", True, Colors.YELLOW)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"VIDAS: {self.lives}", True, Colors.RED)
        self.screen.blit(lives_text, (10, 35))
        
        wave_text = self.font.render(f"WAVE: {self.wave}", True, Colors.CYAN)
        self.screen.blit(wave_text, (250, 10))
        
        enemies_text = self.font.render(f"ENEMIGOS: {len(self.enemies)}", True, Colors.WHITE)
        self.screen.blit(enemies_text, (250, 35))
        
        if self.player:
            health_text = self.font.render(f"SALUD: {self.player.health}", True, Colors.GREEN)
            self.screen.blit(health_text, (500, 10))
            
            power_text = self.font.render(f"PODER: {self.player.power_level}", True, Colors.PURPLE)
            self.screen.blit(power_text, (500, 35))
            
        high_score_text = self.small_font.render(f"RECORD: {self.high_score}", True, Colors.GOLD)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 150, 10))
        
        # Indicador de boss wave
        if self.wave % 5 == 0:
            boss_text = self.font.render("🔥 WAVE DE JEFE 🔥", True, Colors.GOLD)
            boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
            self.screen.blit(boss_text, boss_rect)
        
    def draw_menu(self):
        self.screen.fill(Colors.BLACK)
        
        # Título con efecto
        time = pygame.time.get_ticks() / 1000
        scale = 1 + math.sin(time * 2) * 0.1
        
        title_text = self.title_font.render("⚔️ AKARI WARRIOR ⚔️", True, Colors.GOLD)
        title_scaled = pygame.transform.scale(title_text, 
                                            (int(title_text.get_width() * scale),
                                             int(title_text.get_height() * scale)))
        title_rect = title_scaled.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_scaled, title_rect)
        
        # Estado del gamepad
        gamepad_status = f"🎮 Gamepad: {self.joystick_name}"
        gamepad_color = Colors.GREEN if self.joystick else Colors.RED
        gamepad_text = self.small_font.render(gamepad_status, True, gamepad_color)
        gamepad_rect = gamepad_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(gamepad_text, gamepad_rect)
        
        # Instrucciones
        instructions = [
            "=== CONTROLES ===",
            "",
            "TECLADO:",
            "WASD - Mover (cambia sprite direccional)",
            "FLECHAS/IJKL - Disparar direccional",
            "ESPACIO - Disparar hacia dirección actual",
            "ESC - Pausa",
            "",
            "GAMEPAD:",
            "Stick Izq/D-Pad - Mover",
            "Stick Der - Apuntar y disparar",
            "Botones ABXY - Disparar direccional",
            "Start - Pausa",
            "",
            "¡Coloca sprites en assets/images/ y sonidos en assets/sounds/!",
            "",
            "¡Sobrevive a las waves enemigas!",
            "",
            "PRESIONA ESPACIO o A PARA COMENZAR"
        ]
        
        y_start = 220
        for i, instruction in enumerate(instructions):
            if instruction == "":
                continue
            
            # Colores especiales para títulos
            if "===" in instruction:
                color = Colors.CYAN
            elif "TECLADO:" in instruction or "GAMEPAD:" in instruction:
                color = Colors.YELLOW
            elif "PRESIONA" in instruction:
                color = Colors.GOLD
            elif "assets/" in instruction:
                color = Colors.ORANGE
            else:
                color = Colors.WHITE
                
            text = self.small_font.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 22))
            self.screen.blit(text, text_rect)
            
        # Record
        if self.high_score > 0:
            record_text = self.font.render(f"MEJOR PUNTUACIÓN: {self.high_score}", True, Colors.SILVER)
            record_rect = record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(record_text, record_rect)
            
    def draw_game_over(self):
        self.screen.fill(Colors.BLACK)
        
        # Game Over con efecto
        time = pygame.time.get_ticks() / 1000
        alpha = int(255 * (0.5 + 0.5 * math.sin(time * 3)))
        
        game_over_text = self.title_font.render("💀 GAME OVER 💀", True, Colors.RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Estadísticas finales
        final_score_text = self.font.render(f"Puntuación Final: {self.score}", True, Colors.YELLOW)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(final_score_text, final_score_rect)
        
        wave_text = self.font.render(f"Wave Alcanzada: {self.wave}", True, Colors.CYAN)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(wave_text, wave_rect)
        
        # Nuevo record
        if self.score >= self.high_score:
            new_record_surface = pygame.Surface((400, 40))
            new_record_surface.set_alpha(alpha)
            new_record_text = self.font.render("🏆 ¡NUEVO RÉCORD! 🏆", True, Colors.GOLD)
            new_record_surface.blit(new_record_text, (0, 0))
            new_record_rect = new_record_surface.get_rect(center=(SCREEN_WIDTH // 2, 380))
            self.screen.blit(new_record_surface, new_record_rect)
            
        # Continuar
        continue_text = self.font.render("PRESIONA ESPACIO PARA VOLVER AL MENÚ", True, Colors.WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(continue_text, continue_rect)
        
    def draw_paused(self):
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa con efecto
        time = pygame.time.get_ticks() / 1000
        scale = 1 + math.sin(time * 4) * 0.05
        
        pause_text = self.title_font.render("⏸️ PAUSA ⏸️", True, Colors.CYAN)
        pause_scaled = pygame.transform.scale(pause_text,
                                            (int(pause_text.get_width() * scale),
                                             int(pause_text.get_height() * scale)))
        pause_rect = pause_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_scaled, pause_rect)
        
        resume_text = self.font.render("PRESIONA ESC O ESPACIO PARA CONTINUAR", True, Colors.WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(resume_text, resume_rect)
        
        # Mostrar controles en pausa
        controls_text = self.small_font.render("Gamepad: Start para continuar", True, Colors.LIGHT_GRAY)
        controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(controls_text, controls_rect)
        
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
            
        elif self.state == GameState.PLAYING:
            self.screen.fill(Colors.BLACK)
            
            # Dibujar todos los sprites
            self.all_sprites.draw(self.screen)
            
            # Dibujar barras de vida de enemigos
            for enemy in self.enemies:
                enemy.draw_health_bar(self.screen)
            
            # Dibujar HUD
            self.draw_hud()
            
        elif self.state == GameState.PAUSED:
            self.screen.fill(Colors.BLACK)
            self.all_sprites.draw(self.screen)
            
            # Dibujar barras de vida de enemigos
            for enemy in self.enemies:
                enemy.draw_health_bar(self.screen)
                
            self.draw_hud()
            self.draw_paused()
            
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def run(self):
        print("🎮 Iniciando Akari Warrior...")
        print("📁 Estructura de assets recomendada:")
        print("   assets/images/ - Sprites del juego")
        print("   assets/sounds/ - Efectos de sonido (.wav, .ogg, .mp3)")
        print("   assets/music/ - Música de fondo (.mp3, .ogg, .wav)")
        print("⚔️ ¡Que comience la batalla!")
        
        while self.running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Input
            self.handle_input()
            
            # Update
            self.update()
            
            # Draw
            self.draw()
            
            # FPS
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = AkariWarrior()
    game.run()