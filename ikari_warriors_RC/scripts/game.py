import pygame
from scripts.player import Player
from scripts.utils.constants import *
from scripts.utils.resources import ResourceManager
from scripts.ai.pathfinding import Grid, AStar

class Game:
    """Clase principal que maneja el estado del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.PLAYING  # Por ahora empezamos directo
        self.resource_manager = ResourceManager()
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        
        # Crear jugador
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Crear grid para pathfinding
        grid_width = SCREEN_WIDTH // TILE_SIZE
        grid_height = SCREEN_HEIGHT // TILE_SIZE
        self.grid = Grid(grid_width, grid_height, TILE_SIZE)
        self.pathfinder = AStar(self.grid)
        
        # Crear algunos obstáculos de prueba
        self.create_test_obstacles()
        
        # Variables para debug de pathfinding
        self.show_pathfinding = True
        self.test_path = []
        self.path_start = None
        self.path_end = None
        
        # Inicializar gamepad si está disponible
        self.init_gamepad()
        
    def create_test_obstacles(self):
        """Crea algunos obstáculos para probar el pathfinding"""
        # Crear algunos muros
        obstacles = [
            # Muro horizontal
            (10, 10), (11, 10), (12, 10), (13, 10), (14, 10),
            # Muro vertical
            (20, 5), (20, 6), (20, 7), (20, 8), (20, 9),
            # L shape
            (5, 15), (6, 15), (7, 15), (7, 16), (7, 17),
            # Cuadrado
            (25, 15), (26, 15), (27, 15),
            (25, 16), (27, 16),
            (25, 17), (26, 17), (27, 17),
        ]
        
        for x, y in obstacles:
            self.grid.set_walkable(x, y, False)
        
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
    
    def update(self, dt, events):
        """Actualiza la lógica del juego"""
        if self.state == GameState.PLAYING:
            # Obtener input
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            
            # Manejar eventos específicos
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Toggle pathfinding debug
                        self.show_pathfinding = not self.show_pathfinding
                    elif event.key == pygame.K_c:  # Clear path
                        self.test_path = []
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Click derecho - establecer destino
                        self.path_end = mouse_pos
                        if self.path_start:
                            # Calcular nuevo camino
                            self.test_path = self.pathfinder.find_path(
                                self.path_start, self.path_end
                            )
            
            # Actualizar posición inicial del path (posición del jugador)
            self.path_start = (self.player.pos.x, self.player.pos.y)
            
            # Actualizar jugador con input
            self.player.handle_input(keys, mouse_pos, mouse_buttons, self.gamepad)
            
            # Actualizar todos los sprites
            self.all_sprites.update(dt)
            
            # Verificar colisiones
            self.check_collisions()
            
        elif self.state == GameState.MENU:
            # TODO: Implementar lógica del menú
            pass
            
    def check_collisions(self):
        """Verifica colisiones entre entidades"""
        # TODO: Implementar colisiones
        pass
    
    def draw(self):
        """Dibuja todo en pantalla"""
        # Limpiar pantalla
        self.screen.fill(DARK_GREEN)
        
        if self.state == GameState.PLAYING:
            # Dibujar grid (opcional, para debug)
            if self.show_pathfinding:
                self.draw_grid()
                
            # Dibujar obstáculos
            self.draw_obstacles()
            
            # Dibujar sprites
            self.all_sprites.draw(self.screen)
            
            # Dibujar path de debug
            if self.show_pathfinding and self.test_path:
                self.pathfinder.draw_path(self.screen, self.test_path)
                
            # Dibujar UI
            self.draw_ui()
            
        elif self.state == GameState.MENU:
            # TODO: Dibujar menú
            pass
    
    def draw_grid(self):
        """Dibuja el grid del pathfinding (para debug)"""
        # Líneas verticales
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
            
        # Líneas horizontales
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_obstacles(self):
        """Dibuja los obstáculos del mapa"""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                node = self.grid.get_node(x, y)
                if not node.walkable:
                    rect = pygame.Rect(
                        x * TILE_SIZE, 
                        y * TILE_SIZE, 
                        TILE_SIZE, 
                        TILE_SIZE
                    )
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Dibujar barra de vida
        health_width = int((self.player.health / PLAYER_HEALTH) * 200)
        health_rect = pygame.Rect(10, 10, health_width, 20)
        border_rect = pygame.Rect(10, 10, 200, 20)
        
        pygame.draw.rect(self.screen, RED, health_rect)
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)
        
        # Instrucciones de debug
        if self.show_pathfinding:
            font = pygame.font.Font(None, 24)
            instructions = [
                "P - Toggle grid/pathfinding",
                "Click derecho - Establecer destino",
                "C - Limpiar camino"
            ]
            y = 40
            for text in instructions:
                surf = font.render(text, True, WHITE)
                self.screen.blit(surf, (10, y))
                y += 25
        
        # TODO: Agregar más elementos de UI (munición, score, etc.)
        