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
            self.image = load_sprite("assets/images/enemy_bullet.png", (16, 16), color)
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
        
        # Eliminar si sale de pantalla (con un pequeño margen)
        if (self.rect.x < -50 or self.rect.x > SCREEN_WIDTH + 50 or 
            self.rect.y < -50 or self.rect.y > SCREEN_HEIGHT + 50):
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Cargar sprites del jugador
        self.sprites = {
            'up': load_sprite("assets/images/player_up.png", (64, 64), Colors.CYAN),
            'down': load_sprite("assets/images/player_down.png", (64, 64), Colors.CYAN),
            'left': load_sprite("assets/images/player_left.png", (64, 64), Colors.CYAN),
            'right': load_sprite("assets/images/player_right.png", (64, 64), Colors.CYAN)
        }
        
        # Si no hay sprites direccionales, intentar cargar uno general
        if not os.path.exists("assets/images/player_up.png"):
            default_sprite = load_sprite("assets/images/player.png", (64, 64), Colors.CYAN)
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
        self.power_level = 1 # Nivel de poder de disparo
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
        bullets_fired = [] # ### CAMBIO: Para manejar múltiples balas
        if self.shoot_cooldown <= 0:
            # Si no se especifica dirección, usar la dirección de mirada
            if direction_x is None or direction_y is None:
                direction_x, direction_y = self.facing_direction
            
            # ### CAMBIO: Lógica de disparo según el nivel de poder
            if self.power_level == 1:
                bullet = Bullet(self.rect.centerx, self.rect.centery, 
                                direction_x, direction_y, speed=10, color=Colors.YELLOW)
                bullets_fired.append(bullet)
            elif self.power_level == 2:
                # Dos balas ligeramente separadas
                bullet1 = Bullet(self.rect.centerx - 10, self.rect.centery, 
                                 direction_x, direction_y, speed=10, color=Colors.YELLOW)
                bullet2 = Bullet(self.rect.centerx + 10, self.rect.centery, 
                                 direction_x, direction_y, speed=10, color=Colors.YELLOW)
                bullets_fired.extend([bullet1, bullet2])
            elif self.power_level >= 3:
                # Tres balas en un arco
                angle = math.atan2(-direction_y, direction_x)
                angles = [angle - 0.2, angle, angle + 0.2] # Pequeño arco
                
                for a in angles:
                    bx = math.cos(a)
                    by = -math.sin(a)
                    bullet = Bullet(self.rect.centerx, self.rect.centery, 
                                    bx, by, speed=10, color=Colors.YELLOW)
                    bullets_fired.append(bullet)

            self.shoot_cooldown = max(10 - self.power_level, 5) # Más rápido con más poder
            return bullets_fired
        return [] # ### CAMBIO: Retorna lista vacía si no dispara
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True # Indica que la vida llegó a 0
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__()
        self.enemy_type = enemy_type
        
        # Configurar según tipo
        if enemy_type == "basic":
            self.image = load_sprite("assets/images/enemy.png", (64, 64), Colors.RED)
            self.health = 40
            self.speed = 2
            self.points = 150
        elif enemy_type == "fast":
            self.image = load_sprite("assets/images/enemy_fast.png", (64, 64), Colors.ORANGE)
            self.health = 25
            self.speed = 3
            self.points = 300
        elif enemy_type == "heavy":
            self.image = load_sprite("assets/images/enemy_heavy.png", (64, 64), Colors.PURPLE)
            self.health = 150
            self.speed = 1.5 # ### CAMBIO: Velocidad ajustada para enemigos pesados
            self.points = 500
        elif enemy_type == "shooter":
            self.image = load_sprite("assets/images/enemy_shooter.png", (64, 64), Colors.YELLOW)
            self.health = 100
            self.speed = 2.5
            self.points = 800
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_health = self.health
        self.shoot_cooldown = 0
        self.ai_timer = 0
        self.shoot_interval = 60 # ### CAMBIO: Intervalo base de disparo para shooters/heavy
        
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
        if self.enemy_type in ["shooter", "heavy"] and self.shoot_cooldown <= 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0 and distance < 300: # Solo dispara si el jugador está en rango
                dx /= distance
                dy /= distance
                
                bullet = Bullet(self.rect.centerx, self.rect.centery,
                                dx, dy, speed=5, color=Colors.RED, is_enemy=True)
                self.shoot_cooldown = self.shoot_interval # Reiniciar cooldown
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
        # ### CAMBIO: Aumentado el tamaño del sprite del powerup para mayor visibilidad
        self.image = load_sprite(sprite_path, (32, 32), colors.get(power_type, Colors.WHITE)) 
        
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

        try:
            self.background = pygame.image.load("assets/images/fondo.png")
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
            print("No se pudo cargar el fondo")
        
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
        
        # ### CAMBIO: Posición inicial del jugador para respawn
        self.player_initial_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100) 
        
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
        self.player = Player(self.player_initial_pos[0], self.player_initial_pos[1]) # ### CAMBIO: Usar posición inicial
        self.all_sprites.add(self.player)
        
        # Crear primera wave
        self.spawn_wave()
        
    def spawn_wave(self):
        wave_size = min(5 + self.wave * 2 , 25)
        enemy_types = ['basic']
        
        # ### CAMBIO: Introducción de enemigos más gradual
        if self.wave >= 2: 
            enemy_types.append('fast')
        if self.wave >= 4: 
            enemy_types.append('heavy')
        if self.wave >= 5: 
            enemy_types.append('shooter')
            
        # Música de jefe en waves especiales
        if self.wave % 5 == 0:
            self.sound_manager.play_boss_music()
        else:
            self.sound_manager.play_game_music() # Vuelve a la música de juego si no es oleada de jefe
            
        for _ in range(wave_size):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, 200)
            enemy_type = random.choice(enemy_types)
            
            enemy = Enemy(x, y, enemy_type)
            speed_multiplier = 1 + (self.wave - 1) * 0.1 # ### CAMBIO: Multiplicador de velocidad reducido
            enemy.speed *= speed_multiplier
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
                    shoot_dx, shoot_dy = self.player.facing_direction # ### CAMBIO: Dispara en la dirección en la que mira el jugador
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
                    if self.joystick.get_button(0) and not shot_fired: # Solo usa si no se ha disparado ya con el stick
                        shoot_dx, shoot_dy = self.last_shot_direction
                        shot_fired = True
                    
                    # Botones de cara para direcciones específicas (si no se usa el stick derecho)
                    if not shot_fired and self.joystick.get_numbuttons() >= 4:
                        if self.joystick.get_button(3):  # Y/Triangle - Arriba
                            shoot_dx, shoot_dy = 0, -1
                            shot_fired = True
                        elif self.joystick.get_button(0):  # A/X - Abajo (puede entrar en conflicto con el disparo por defecto)
                             if self.last_shot_direction != [0,1]: # Previene doble disparo en A
                                shoot_dx, shoot_dy = 0, 1
                                shot_fired = True
                        elif self.joystick.get_button(2):  # X/Square - Izquierda
                            shoot_dx, shoot_dy = -1, 0
                            shot_fired = True
                        elif self.joystick.get_button(1):  # B/Circle - Derecha
                            shoot_dx, shoot_dy = 1, 0
                            shot_fired = True
                        
                    # Gatillos para disparo rápido (si no se usan otros métodos)
                    if self.joystick.get_numaxes() >= 5 and not shot_fired:
                        # RT/R2 para disparar
                        trigger = self.joystick.get_axis(4)  # O axis 5 según el gamepad
                        if trigger > 0.5:
                            shoot_dx, shoot_dy = self.last_shot_direction
                            shot_fired = True
                
                # Ejecutar disparo
                if shot_fired:
                    bullets_fired = self.player.shoot(shoot_dx, shoot_dy) # ### CAMBIO: Ahora shoot devuelve una lista
                    for bullet in bullets_fired:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                    if bullets_fired:
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
                    if random.random() < 0.2: # ### CAMBIO: Tasa de aparición de powerups ligeramente reducida
                        powerup_type = random.choice(['health', 'power', 'speed', 'multi']) # ### CAMBIO: Añadido 'multi'
                        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)
                else:
                    self.sound_manager.play_sound('hit')
                break # La bala solo golpea a un enemigo
                
        # Colisiones: balas enemigas con jugador
        if self.player:
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_bullets:
                self.sound_manager.play_sound('hurt')
                if self.player.take_damage(20 * len(hit_bullets)): # Daño basado en el número de balas
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                        self.save_high_score()
                        self.sound_manager.play_sound('game_over')
                        self.sound_manager.stop_music()
                    else:
                        # ### CAMBIO: Pausar y reaparecer al perder una vida
                        self.player.health = self.player.max_health # Restablecer vida
                        self.player.rect.center = self.player_initial_pos # Volver a la posición inicial
                        self.state = GameState.PAUSED # Pausar el juego
                        self.sound_manager.pause_music() # Pausar la música
                        
            # Colisiones: enemigos con jugador
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in hit_enemies: # El jugador recibe daño y el enemigo es eliminado
                if self.player.take_damage(30):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = GameState.GAME_OVER
                        self.save_high_score()
                        self.sound_manager.play_sound('game_over')
                        self.sound_manager.stop_music()
                    else:
                        # ### CAMBIO: Pausar y reaparecer al perder una vida
                        self.player.health = self.player.max_health # Restablecer vida
                        self.player.rect.center = self.player_initial_pos # Volver a la posición inicial
                        self.state = GameState.PAUSED # Pausar el juego
                        self.sound_manager.pause_music() # Pausar la música
                enemy.kill() # El enemigo es destruido al colisionar
                self.sound_manager.play_sound('hurt') # Reproducir sonido de daño para el jugador
                        
            # Colisiones: powerups con jugador
            hit_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in hit_powerups:
                self.sound_manager.play_sound('powerup')
                if powerup.power_type == 'health':
                    # ### CAMBIO: Aumentar vida del jugador
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.power_type == 'power':
                    self.player.power_level += 1
                    # Limitar nivel de poder
                    if self.player.power_level > 3: # ### CAMBIO: Límite de nivel de poder
                        self.player.power_level = 3 
                elif powerup.power_type == 'speed':
                    self.player.speed = min(self.player.speed + 1, 10) # ### CAMBIO: Velocidad máxima 10
                elif powerup.power_type == 'multi':
                    self.player.power_level += 1 # ### CAMBIO: Multi-shot también aumenta el nivel de poder
                    if self.player.power_level > 3:
                        self.player.power_level = 3

        # Lógica de oleadas
        if len(self.enemies) == 0 and self.state == GameState.PLAYING:
            self.wave_timer += 1
            if self.wave_timer > FPS * 3: # 3 segundos entre oleadas
                self.wave += 1
                self.spawn_wave()
                self.wave_timer = 0
                self.sound_manager.play_sound('wave_complete')

    # ### CAMBIO: Método para dibujar todos los elementos del juego
    def draw(self):
        self.screen.fill(Colors.BLACK) # Fondo por defecto si la imagen no se carga
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        if self.state == GameState.MENU:
            self.show_menu_screen()
        elif self.state == GameState.PLAYING:
            self.all_sprites.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw_health_bar(self.screen)
            self.draw_hud()
        elif self.state == GameState.PAUSED:
            self.all_sprites.draw(self.screen) # Dibujar sprites incluso en pausa
            for enemy in self.enemies:
                enemy.draw_health_bar(self.screen)
            self.draw_hud()
            self.show_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self.show_game_over_screen()
            
        pygame.display.flip()
        
    # ### CAMBIO: Método para dibujar el HUD (información en pantalla)
    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, Colors.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, Colors.WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))
        
        # Wave
        wave_text = self.font.render(f"Wave: {self.wave}", True, Colors.WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 10))
        
        # Health bar
        if self.player:
            bar_width = 200
            bar_height = 20
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = SCREEN_HEIGHT - 30
            
            pygame.draw.rect(self.screen, Colors.RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * (self.player.health / self.player.max_health))
            pygame.draw.rect(self.screen, Colors.GREEN, (bar_x, bar_y, health_width, bar_height))
            
            health_text = self.small_font.render(f"HP: {self.player.health}/{self.player.max_health}", True, Colors.WHITE)
            self.screen.blit(health_text, (bar_x + bar_width // 2 - health_text.get_width() // 2, bar_y + bar_height // 2 - health_text.get_height() // 2))

    # ### CAMBIO: Pantalla de menú
    def show_menu_screen(self):
        title_text = self.title_font.render("AKARI WARRIOR", True, Colors.GOLD)
        start_text = self.font.render("Press SPACE or A/X to Start", True, Colors.WHITE)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, Colors.SILVER)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(high_score_text, high_score_rect)
        
        # Display joystick info
        joystick_info = self.small_font.render(f"Gamepad: {self.joystick_name}", True, Colors.LIGHT_GRAY)
        joystick_rect = joystick_info.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(joystick_info, joystick_rect)

    # ### CAMBIO: Pantalla de pausa
    def show_pause_screen(self):
        # Oscurecer el fondo ligeramente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Negro con 150 de transparencia (0-255)
        self.screen.blit(overlay, (0,0))

        pause_text = self.title_font.render("PAUSED", True, Colors.WHITE)
        resume_text = self.font.render("Press ESC or START/A to Resume", True, Colors.WHITE)
        
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)

    # ### CAMBIO: Pantalla de Game Over
    def show_game_over_screen(self):
        game_over_text = self.title_font.render("GAME OVER", True, Colors.RED)
        score_text = self.font.render(f"Your Score: {self.score}", True, Colors.WHITE)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, Colors.GOLD)
        restart_text = self.font.render("Press SPACE or A/X to return to Menu", True, Colors.WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_score_text, high_score_rect)
        self.screen.blit(restart_text, restart_rect)

    # ### CAMBIO: Bucle principal del juego
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Manejar eventos de botón de joystick por separado para evitar entrada continua
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.state == GameState.MENU and event.button == 0: # Botón A/X
                        self.start_game()
                    elif self.state == GameState.PLAYING and event.button == 7: # Botón Start
                        self.state = GameState.PAUSED
                        self.sound_manager.pause_music()
                    elif self.state == GameState.PAUSED and (event.button == 7 or event.button == 0):
                        self.state = GameState.PLAYING
                        self.sound_manager.unpause_music()
                    elif self.state == GameState.GAME_OVER and event.button == 0:
                        self.state = GameState.MENU
                        self.sound_manager.play_menu_music()

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = AkariWarrior()
    game.run()