"Ikari Warriors RC"



import pygame
import sys

from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
def main():
    # Inicializar Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Configurar la ventana
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    # Bucle principal
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time en segundos
        
        # Manejar eventos
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Actualizar y dibujar
        game.update(dt, events)
        game.draw()
        
        pygame.display.flip()
    
    # Cerrar el juego
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()