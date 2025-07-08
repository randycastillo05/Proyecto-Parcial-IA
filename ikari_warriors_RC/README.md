# Proyecto-parcial-IA

## Randy Castillo

## 21-EISN-2-007

## ⚔ Akari Warrior

*El guerrero de las dimensiones*

Un emocionante juego de acción y supervivencia desarrollado en Python con Pygame, donde debes enfrentarte a waves infinitas de enemigos usando estrategia, reflejos y poder de fuego direccional.

![Akari Warrior Banner](https://img.shields.io/badge/Akari-Warrior-gold?style=for-the-badge&logo=gamepad&logoColor=white)
![Python Version](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green?style=flat-square&logo=pygame)
![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)

## 🎮 Características del Juego

### 🔥 *Sistema de Combate Avanzado*
- *Disparo direccional completo*: Dispara en 8 direcciones usando flechas o IJKL
- *4 tipos de enemigos únicos* con IA y comportamientos diferentes
- *Sistema de waves progresivas* con dificultad creciente
- *Colisiones precisas* con sistema de sprites optimizado

### 🎯 *Tipos de Enemigos*
| Tipo | Color | Salud | Velocidad | Habilidad Especial |
|------|-------|-------|-----------|-------------------|
| *Básico* | 🔴 Rojo | 30 HP | Normal | Persecución directa |
| *Rápido* | 🟠 Naranja | 15 HP | Muy alta | Movimiento zigzag |
| *Pesado* | 🟣 Morado | 80 HP | Lenta | Alta resistencia |
| *Tirador* | 🟡 Amarillo | 40 HP | Media | Dispara proyectiles |

### 🎪 *Sistema de PowerUps*
- 🟢 *Salud*: Restaura 30 HP
- 🟡 *Poder*: Aumenta nivel de poder
- 🔵 *Velocidad*: Incrementa velocidad de movimiento
- 🟣 *Multi*: Activa disparo múltiple

### 📊 *Sistema de Progresión*
- Puntuación basada en tipo de enemigo y wave
- Multiplicadores por supervivencia
- Guardado automático de récord personal
- Sistema de vidas con regeneración

## 🎮 Controles

### *Movimiento*
- WASD - Mover al jugador
- El jugador se mantiene automáticamente dentro de los límites

### *Combate*
- ↑↓←→ (Flechas) - Disparar direccional
- IJKL - Disparar direccional (alternativo)
- ESPACIO - Disparar hacia arriba (por defecto)

### *Sistema*
- ESC - Pausa/Volver al menú
- ENTER/ESPACIO - Confirmar en menús

## 🚀 Instalación y Ejecución

### *Requisitos*
- Python 3.7 o superior
- Pygame 2.0 o superior

### *Instalación Rápida*
bash
# Clonar o descargar el proyecto
git clone [(https://github.com/randycastillo05/Proyecto-Parcial-IA.git)]
cd akari-warrior

# Instalar dependencias
pip install pygame

# Ejecutar el juego
python main.py


### *Instalación Completa con Assets*
bash
# Instalar pygame
pip install pygame

# Crear estructura de carpetas (opcional)
mkdir -p assets/images
mkdir -p assets/sounds
mkdir -p assets/music

# Agregar assets personalizados (opcional)
# - assets/images/: sprites del juego
# - assets/sounds/: efectos de sonido
# - assets/music/: música de fondo


## 📁 Estructura del Proyecto


akari-warrior/
├── main.py                 # Archivo principal del juego
├── player.py              # Clase del jugador con sprites direccionales
├── enemy.py               # Enemigos con IA y árbol de comportamiento
├── level.py               # Sistema de niveles y obstáculos
├── README.md              # Este archivo
├── assets/                # Recursos del juego (opcional)
│   ├── images/           # Sprites y gráficos
│   ├── sounds/           # Efectos de sonido
│   └── music/            # Música de fondo
└── saves/                # Archivos de guardado
    └── akari_warrior_high_score.txt


## 🎯 Cómo Jugar

### *Objetivo*
Sobrevive el mayor tiempo posible enfrentándote a waves infinitas de enemigos. Cada wave aumenta la dificultad y el número de enemigos.

### *Estrategias*
1. *Mantén la distancia* - Los enemigos tiradores son peligrosos de cerca
2. *Usa el movimiento* - El movimiento constante evita que te rodeen
3. *Prioriza objetivos* - Elimina primero a los enemigos rápidos y tiradores
4. *Recolecta PowerUps* - Especialmente salud y velocidad en waves avanzadas
5. *Controla el espacio* - Usa los bordes de pantalla para canalizar enemigos

### *Sistema de Puntuación*
- *Enemigo Básico*: 100 puntos
- *Enemigo Rápido*: 150 puntos  
- *Enemigo Pesado*: 300 puntos
- *Enemigo Tirador*: 200 puntos
- *Bonus por Wave*: 500 puntos
- *Multiplicador*: Puntos × Número de Wave

## 🛠 Características Técnicas

### *Arquitectura del Código*
- *Programación Orientada a Objetos* con clases especializadas
- *Sistema de Sprites de Pygame* para manejo eficiente de gráficos
- *Máquina de Estados* para gestión de menús y gameplay
- *Sistema de Colisiones* optimizado con grupos de sprites
- *Modularidad* con archivos separados por funcionalidad

### *Sistemas Implementados*
- ✅ Sistema de disparo direccional multidireccional
- ✅ IA de enemigos con comportamientos únicos
- ✅ Sistema de waves con escalado de dificultad
- ✅ PowerUps con efectos temporales y permanentes
- ✅ Sistema de puntuación y guardado de récords
- ✅ HUD informativo en tiempo real
- ✅ Estados de juego (Menú, Jugando, Pausa, Game Over)

### *Optimizaciones*
- Uso eficiente de pygame.sprite.Group() para colisiones
- Eliminación automática de sprites fuera de pantalla
- Sistema de cooldowns para prevenir spam
- Actualizaciones diferenciadas por tipo de sprite

## 🎨 Personalización

### *Añadir Assets Visuales*
El juego soporta sprites personalizados. Coloca tus imágenes en:

assets/images/
├── player.png           # Jugador (32x32px)
├── player_up.png        # Jugador mirando arriba
├── player_down.png      # Jugador mirando abajo
├── player_left.png      # Jugador mirando izquierda
├── player_right.png     # Jugador mirando derecha
├── enemy.png            # Enemigo básico (24x24px)
├── enemy_alert.png      # Enemigo en estado de alerta
├── bullet.png           # Bala del jugador (8x16px)
├── enemy_bullet.png     # Bala enemiga (8x8px)
├── wall.png             # Textura de pared
└── floor.png            # Textura del suelo


### *Añadir Audio*

assets/sounds/
├── shoot.wav            # Sonido de disparo
└── hit.wav              # Sonido de impacto

assets/music/
└── background.mp3       # Música de fondo


### *Configuración*
Modifica las constantes en main.py:
python
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700  # Resolución
FPS = 60                                  # Frames por segundo
PLAYER_SPEED = 5                         # Velocidad del jugador
ENEMY_SPEED = 2                          # Velocidad base de enemigos


## 🐛 Solución de Problemas

### *Error: ModuleNotFoundError: No module named 'pygame'*
bash
pip install pygame
# o si usas conda:
conda install pygame


### *El juego va muy lento*
- Reduce el FPS en main.py: FPS = 30
- Reduce la resolución: SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

### *No se cargan los sprites*
- El juego funciona sin assets usando colores sólidos
- Verifica que las imágenes estén en assets/images/
- Revisa que los archivos tengan los nombres exactos

### *Error al guardar puntuación*
- Asegúrate de que el directorio sea escribible
- El archivo se crea automáticamente: akari_warrior_high_score.txt

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes ayudar con:

- 🎨 *Assets gráficos*: Sprites, efectos visuales, animaciones
- 🎵 *Audio*: Música de fondo, efectos de sonido
- 🎮 *Gameplay*: Nuevos tipos de enemigos, powerups, mecánicas
- 🐛 *Bugs*: Reportes de errores y correcciones
- 📚 *Documentación*: Mejoras al README, comentarios en código

### *Cómo Contribuir*
1. Fork del proyecto
2. Crea una rama para tu feature (git checkout -b feature/nueva-caracteristica)
3. Commit tus cambios (git commit -am 'Añadir nueva característica')
4. Push a la rama (git push origin feature/nueva-caracteristica)
5. Crea un Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver LICENSE para más detalles.

## 🏆 Créditos

- *Desarrollador Principal*: [Tu Nombre]
- *Motor de Juego*: Pygame Community
- *Inspiración*: Juegos clásicos de arcade y shoot 'em up

## 🎯 Roadmap

### *Versión Actual (v2.0)*
- ✅ Sistema de disparo direccional
- ✅ 4 tipos de enemigos con IA
- ✅ Sistema de waves progresivas
- ✅ PowerUps funcionales
- ✅ Sistema de puntuación y guardado

### *Próximas Versiones*
- 🔄 *v2.1*: Boss fights cada 5 waves
- 🔄 *v2.2*: Sistema de mejoras permanentes
- 🔄 *v2.3*: Múltiples armas y tipos de disparo
- 🔄 *v2.4*: Co-op local para 2 jugadores
- 🔄 *v2.5*: Niveles con obstáculos destructibles

---

*¡Disfruta jugando Akari Warrior y que tengas épicas batallas! ⚔🔥*

Para reportar bugs o sugerir características, abre un issue en el repositorio.
