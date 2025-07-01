import pygame
import math
from scripts.utils.constants import *

class Menu:
    """Menú principal del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Opciones del menú
        self.options = ["Iniciar Juego", "Controles", "Créditos", "Salir"]
        self.selected_option = 0
        
        # Estado del menú
        self.showing_controls = False
        self.showing_credits = False
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 72)
        self.option_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        # Animación
        self.animation_timer = 0
        self.star_positions = self.create_stars()
        
        # Control con gamepad
        self.gamepad = None
        self.init_gamepad()
        self.gamepad_cooldown = 0
        
        # Sonidos (TODO: cargar sonidos reales)
        self.select_sound = None
        self.confirm_sound = None
        
    def init_gamepad(self):
        """Inicializa el gamepad si está disponible"""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
    
    def create_stars(self):
        """Crea estrellas para el fondo animado"""
        import random
        stars = []
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.5, 2.0)
            size = random.randint(1, 3)
            stars.append([x, y, speed, size])
        return stars
    
    def handle_event(self, event):
        """Maneja los eventos del menú"""
        if self.showing_controls or self.showing_credits:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.showing_controls = False
                    self.showing_credits = False
                    return None
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:  # B/Circle
                    self.showing_controls = False
                    self.showing_credits = False
                    return None
            
            return None
        
        # Navegación con teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.play_select_sound()
                
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.play_select_sound()
                
            elif event.key == pygame.K_RETURN:
                return self.select_option()
        
        # Navegación con gamepad
        if event.type == pygame.JOYAXISMOTION and self.gamepad:
            if event.axis == 1:  # Eje Y del stick izquierdo
                if abs(event.value) > 0.5 and self.gamepad_cooldown <= 0:
                    if event.value < 0:  # Arriba
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                        self.play_select_sound()
                    else:  # Abajo
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                        self.play_select_sound()
                    self.gamepad_cooldown = 0.3
        
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A/X
                return self.select_option()
        
        return None
    
    def select_option(self):
        """Ejecuta la opción seleccionada"""
        self.play_confirm_sound()
        
        if self.selected_option == 0:  # Iniciar Juego
            return "start"
        elif self.selected_option == 1:  # Controles
            self.showing_controls = True
            return None
        elif self.selected_option == 2:  # Créditos
            self.showing_credits = True
            return None
        elif self.selected_option == 3:  # Salir
            return "quit"
        
        return None
    
    def update(self, dt):
        """Actualiza el menú"""
        # Actualizar animación
        self.animation_timer += dt
        
        # Actualizar cooldown del gamepad
        if self.gamepad_cooldown > 0:
            self.gamepad_cooldown -= dt
        
        # Actualizar estrellas del fondo
        for star in self.star_positions:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = -10
                star[0] = pygame.time.get_ticks() % SCREEN_WIDTH
    
    def draw(self):
        """Dibuja el menú"""
        # Fondo
        self.screen.fill(BLACK)
        
        # Dibujar estrellas animadas
        self.draw_stars()
        
        if self.showing_controls:
            self.draw_controls()
        elif self.showing_credits:
            self.draw_credits()
        else:
            self.draw_main_menu()
    
    def draw_main_menu(self):
        """Dibuja el menú principal"""
        # Título con efecto
        title_text = "IKARI WARRIORS"
        title_color = self.get_animated_color()
        title_surf = self.title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 150))
        
        # Sombra del título
        shadow_surf = self.title_font.render(title_text, True, (50, 50, 50))
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH//2 + 3, 153))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(title_surf, title_rect)
        
        # Subtítulo
        subtitle = self.small_font.render("Clone Edition", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Opciones del menú
        y_start = 300
        for i, option in enumerate(self.options):
            y = y_start + i * 60
            
            # Color y tamaño según selección
            if i == self.selected_option:
                # Efecto de pulsación
                scale = 1.0 + math.sin(self.animation_timer * 5) * 0.1
                color = WHITE
                
                # Indicadores de selección
                arrow_offset = math.sin(self.animation_timer * 3) * 10
                left_arrow = self.option_font.render(">", True, YELLOW)
                right_arrow = self.option_font.render("<", True, YELLOW)
                
                text_surf = self.option_font.render(option, True, color)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
                
                left_rect = left_arrow.get_rect(right=text_rect.left - 20 - arrow_offset)
                left_rect.centery = y
                right_rect = right_arrow.get_rect(left=text_rect.right + 20 + arrow_offset)
                right_rect.centery = y
                
                self.screen.blit(left_arrow, left_rect)
                self.screen.blit(right_arrow, right_rect)
            else:
                color = GRAY
                text_surf = self.option_font.render(option, True, color)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
            
            self.screen.blit(text_surf, text_rect)
        
        # Instrucciones
        instructions = self.small_font.render("↑↓ Navegar - ENTER Seleccionar", True, WHITE)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, inst_rect)
    
    def draw_controls(self):
        """Dibuja la pantalla de controles"""
        # Título
        title = self.title_font.render("CONTROLES", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Controles
        controls = [
            ("TECLADO:", ""),
            ("", ""),
            ("W A S D / Flechas", "Mover"),
            ("Mouse", "Apuntar"),
            ("Click Izquierdo", "Disparar"),
            ("ESC", "Pausa"),
            ("", ""),
            ("GAMEPAD:", ""),
            ("", ""),
            ("Stick Izquierdo", "Mover"),
            ("Stick Derecho", "Apuntar"),
            ("RT / R2", "Disparar"),
            ("Start", "Pausa"),
            ("", ""),
            ("ESC para volver", "")
        ]
        
        y = 180
        for key, action in controls:
            if key:
                key_surf = self.small_font.render(key, True, YELLOW)
                key_rect = key_surf.get_rect(right=SCREEN_WIDTH//2 - 20, centery=y)
                self.screen.blit(key_surf, key_rect)
            
            if action:
                action_surf = self.small_font.render(action, True, WHITE)
                action_rect = action_surf.get_rect(left=SCREEN_WIDTH//2 + 20, centery=y)
                self.screen.blit(action_surf, action_rect)
            
            y += 35
    
    def draw_credits(self):
        """Dibuja la pantalla de créditos"""
        # Título
        title = self.title_font.render("CRÉDITOS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Créditos
        credits = [
            ("Desarrollado por:", "[Tu nombre]"),
            ("Matrícula:", "[Tu matrícula]"),
            ("", ""),
            ("Juego inspirado en:", "Ikari Warriors (SNK, 1986)"),
            ("", ""),
            ("Tecnologías:", ""),
            ("Engine:", "Pygame"),
            ("Lenguaje:", "Python"),
            ("IA:", "Árbol de Comportamiento + A*"),
            ("", ""),
            ("Agradecimientos especiales:", ""),
            ("Profesor:", "[Nombre del profesor]"),
            ("", ""),
            ("ESC para volver", "")
        ]
        
        y = 180
        for label, value in credits:
            if label and value:
                label_surf = self.small_font.render(label, True, YELLOW)
                value_surf = self.small_font.render(value, True, WHITE)
                
                total_width = label_surf.get_width() + value_surf.get_width() + 10
                x_start = (SCREEN_WIDTH - total_width) // 2
                
                self.screen.blit(label_surf, (x_start, y))
                self.screen.blit(value_surf, (x_start + label_surf.get_width() + 10, y))
            elif label:
                text_surf = self.small_font.render(label, True, WHITE)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
                self.screen.blit(text_surf, text_rect)
            
            y += 35
    
    def draw_stars(self):
        """Dibuja las estrellas del fondo"""
        for x, y, speed, size in self.star_positions:
            brightness = int(128 + math.sin(self.animation_timer * speed) * 127)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
    
    def get_animated_color(self):
        """Obtiene un color animado para efectos"""
        r = int(128 + math.sin(self.animation_timer * 2) * 127)
        g = int(128 + math.sin(self.animation_timer * 2 + 2) * 127)
        b = int(128 + math.sin(self.animation_timer * 2 + 4) * 127)
        return (r, g, b)
    
    def play_select_sound(self):
        """Reproduce el sonido de selección"""
        if self.select_sound:
            self.select_sound.play()
    
    def play_confirm_sound(self):
        """Reproduce el sonido de confirmación"""
        if self.confirm_sound:
            self.confirm_sound.play()