# Configuración de pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Ikari Warriors RC"

# Colores (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (34, 139, 34)

# Configuración del jugador
PLAYER_SPEED = 200  # Píxeles por segundo
PLAYER_HEALTH = 100
PLAYER_SIZE = 32

# Configuración de enemigos
ENEMY_SPEED = 100
ENEMY_SIGHT_RANGE = 200
ENEMY_SHOOT_RANGE = 150
ENEMY_HEALTH = 50

# Configuración de armas
BULLET_SPEED = 500
BULLET_DAMAGE = 25
SHOOT_COOLDOWN = 0.3  # Segundos entre disparos

# Configuración del mapa
TILE_SIZE = 32
MAP_WIDTH = 40  # Tiles
MAP_HEIGHT = 30  # Tiles

# Estados del juego
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

# Tipos de enemigos
class EnemyType:
    SOLDIER = "soldier"
    ELITE = "elite"
    SNIPER = "sniper"
    KAMIKAZE = "kamikaze"
    OFFICER = "officer"

# Direcciones
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)