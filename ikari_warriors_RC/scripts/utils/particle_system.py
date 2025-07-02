import pygame
import random
import math

class Particle:
    """Partícula individual para efectos visuales"""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=0, fade=True, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = list(color)
        self.original_color = list(color)
        self.size = size
        self.original_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.fade = fade
        self.shrink = shrink
        self.alive = True
        
    def update(self, dt):
        """Actualiza la partícula"""
        if not self.alive:
            return
            
        # Movimiento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Gravedad
        self.vy += self.gravity * dt
        
        # Actualizar vida
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.alive = False
            return
        
        # Calcular progreso (1 = recién creada, 0 = a punto de morir)
        progress = self.lifetime / self.max_lifetime
        
        # Fade out
        if self.fade:
            alpha = int(255 * progress)
            self.color[3] = alpha if len(self.color) > 3 else None
            
        # Encoger
        if self.shrink:
            self.size = self.original_size * progress
    
    def draw(self, screen):
        """Dibuja la partícula"""
        if self.alive and self.size > 0:
            # Crear superficie con alpha si es necesario
            if len(self.color) > 3 and self.color[3] < 255:
                surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, self.color[:3] + [self.color[3]], 
                                 (int(self.size), int(self.size)), int(self.size))
                screen.blit(surf, (self.x - self.size, self.y - self.size))
            else:
                pygame.draw.circle(screen, self.color[:3], 
                                 (int(self.x), int(self.y)), int(self.size))


class ParticleSystem:
    """Sistema de partículas para efectos especiales"""
    
    def __init__(self):
        self.particles = []
        self.emitters = []
        
    def update(self, dt):
        """Actualiza todas las partículas y emisores"""
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # Actualizar emisores
        for emitter in self.emitters[:]:
            emitter.update(dt)
            if not emitter.active and len(emitter.particles) == 0:
                self.emitters.remove(emitter)
    
    def draw(self, screen):
        """Dibuja todas las partículas"""
        for particle in self.particles:
            particle.draw(screen)
            
        for emitter in self.emitters:
            emitter.draw(screen)
    
    def add_particle(self, particle):
        """Añade una partícula al sistema"""
        self.particles.append(particle)
    
    def add_emitter(self, emitter):
        """Añade un emisor al sistema"""
        self.emitters.append(emitter)
        
    def clear(self):
        """Limpia todas las partículas"""
        self.particles.clear()
        self.emitters.clear()
    
    # Efectos predefinidos
    
    def create_explosion(self, x, y, intensity=1.0, color_base=(255, 200, 0)):
        """Crea una explosión de partículas"""
        # Chispas principales
        for i in range(int(20 * intensity)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = list(color_base) + [255]
            # Variar el color
            color[0] = min(255, color[0] + random.randint(-30, 30))
            color[1] = min(255, color[1] + random.randint(-30, 30))
            
            size = random.uniform(2, 5) * intensity
            lifetime = random.uniform(0.3, 0.8)
            
            particle = Particle(x, y, vx, vy, color, size, lifetime, 
                              gravity=200, fade=True, shrink=True)
            self.add_particle(particle)
        
        # Humo
        for i in range(int(10 * intensity)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 60)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 30  # Tiende a subir
            
            gray = random.randint(50, 100)
            color = [gray, gray, gray, 200]
            
            size = random.uniform(5, 10) * intensity
            lifetime = random.uniform(0.5, 1.2)
            
            particle = Particle(x, y, vx, vy, color, size, lifetime,
                              gravity=-50, fade=True, shrink=False)
            self.add_particle(particle)
    
    def create_blood_splatter(self, x, y, direction_angle, intensity=1.0):
        """Crea salpicadura de sangre"""
        for i in range(int(15 * intensity)):
            # Dispersión en la dirección del impacto
            angle = direction_angle + random.uniform(-0.5, 0.5)
            speed = random.uniform(50, 200) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Color rojo con variaciones
            red = random.randint(150, 255)
            color = [red, 0, 0, 255]
            
            size = random.uniform(1, 3) * intensity
            lifetime = random.uniform(0.3, 0.6)
            
            particle = Particle(x, y, vx, vy, color, size, lifetime,
                              gravity=300, fade=True, shrink=True)
            self.add_particle(particle)
    
    def create_muzzle_flash(self, x, y, angle):
        """Crea destello de disparo"""
        # Flash principal
        for i in range(5):
            spread = random.uniform(-0.2, 0.2)
            flash_angle = angle + spread
            speed = random.uniform(100, 200)
            vx = math.cos(flash_angle) * speed
            vy = math.sin(flash_angle) * speed
            
            color = [255, 255, random.randint(200, 255), 255]
            size = random.uniform(3, 5)
            lifetime = 0.1
            
            particle = Particle(x, y, vx, vy, color, size, lifetime,
                              fade=True, shrink=True)
            self.add_particle(particle)
        
        # Humo del cañón
        for i in range(3):
            smoke_angle = angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(20, 40)
            vx = math.cos(smoke_angle) * speed
            vy = math.sin(smoke_angle) * speed
            
            gray = random.randint(100, 150)
            color = [gray, gray, gray, 150]
            size = random.uniform(2, 4)
            lifetime = 0.3
            
            particle = Particle(x, y, vx, vy, color, size, lifetime,
                              gravity=-20, fade=True, shrink=False)
            self.add_particle(particle)
    
    def create_spark_trail(self, x, y, vx, vy):
        """Crea rastro de chispas (para balas)"""
        # Chispa amarilla
        color = [255, random.randint(200, 255), 0, 255]
        size = random.uniform(1, 2)
        lifetime = 0.2
        
        # Añadir algo de aleatoriedad
        vx += random.uniform(-20, 20)
        vy += random.uniform(-20, 20)
        
        particle = Particle(x, y, vx * 0.3, vy * 0.3, color, size, lifetime,
                          fade=True, shrink=True)
        self.add_particle(particle)
    
    def create_powerup_sparkle(self, x, y, color=(255, 255, 0)):
        """Crea destellos para power-ups"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(20, 50)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 20
        
        particle_color = list(color) + [255]
        size = random.uniform(2, 4)
        lifetime = random.uniform(0.5, 1.0)
        
        particle = Particle(x, y, vx, vy, particle_color, size, lifetime,
                          gravity=-50, fade=True, shrink=True)
        self.add_particle(particle)
    
    def create_smoke_puff(self, x, y, size=1.0):
        """Crea bocanada de humo"""
        for i in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(10, 30)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 20
            
            gray = random.randint(80, 120)
            color = [gray, gray, gray, 150]
            particle_size = random.uniform(3, 6) * size
            lifetime = random.uniform(0.5, 1.0)
            
            particle = Particle(x, y, vx, vy, color, particle_size, lifetime,
                              gravity=-30, fade=True, shrink=False)
            self.add_particle(particle)
    
    def create_teleport_effect(self, x, y):
        """Crea efecto de teletransporte"""
        # Anillo expandiéndose
        for i in range(20):
            angle = (i / 20) * math.pi * 2
            distance = 5
            px = x + math.cos(angle) * distance
            py = y + math.sin(angle) * distance
            
            vx = math.cos(angle) * 100
            vy = math.sin(angle) * 100
            
            color = [100, 200, 255, 255]
            size = 3
            lifetime = 0.5
            
            particle = Particle(px, py, vx, vy, color, size, lifetime,
                              fade=True, shrink=True)
            self.add_particle(particle)


class ParticleEmitter:
    """Emisor de partículas continuo"""
    
    def __init__(self, x, y, emission_rate=10, lifetime=-1):
        self.x = x
        self.y = y
        self.emission_rate = emission_rate  # Partículas por segundo
        self.lifetime = lifetime  # -1 = infinito
        self.elapsed = 0
        self.emission_timer = 0
        self.active = True
        self.particles = []
        
    def update(self, dt):
        """Actualiza el emisor"""
        if not self.active:
            # Solo actualizar partículas existentes
            for particle in self.particles[:]:
                particle.update(dt)
                if not particle.alive:
                    self.particles.remove(particle)
            return
            
        self.elapsed += dt
        self.emission_timer += dt
        
        # Verificar si debe detenerse
        if self.lifetime > 0 and self.elapsed >= self.lifetime:
            self.active = False
            return
        
        # Emitir nuevas partículas
        particles_to_emit = int(self.emission_timer * self.emission_rate)
        self.emission_timer -= particles_to_emit / self.emission_rate
        
        for i in range(particles_to_emit):
            particle = self.create_particle()
            if particle:
                self.particles.append(particle)
        
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Dibuja las partículas del emisor"""
        for particle in self.particles:
            particle.draw(screen)
    
    def create_particle(self):
        """Método a sobrescribir para crear partículas específicas"""
        pass
    
    def stop(self):
        """Detiene la emisión de nuevas partículas"""
        self.active = False
    
    def set_position(self, x, y):
        """Actualiza la posición del emisor"""
        self.x = x
        self.y = y


class FireEmitter(ParticleEmitter):
    """Emisor de fuego"""
    
    def __init__(self, x, y):
        super().__init__(x, y, emission_rate=30)
        
    def create_particle(self):
        # Posición con algo de dispersión
        px = self.x + random.uniform(-5, 5)
        py = self.y + random.uniform(-2, 2)
        
        # Velocidad hacia arriba con dispersión
        vx = random.uniform(-20, 20)
        vy = random.uniform(-80, -40)
        
        # Color de fuego (amarillo a rojo)
        if random.random() < 0.3:
            color = [255, random.randint(200, 255), 0, 255]  # Amarillo
        else:
            color = [255, random.randint(100, 150), 0, 255]  # Naranja/Rojo
            
        size = random.uniform(2, 4)
        lifetime = random.uniform(0.3, 0.6)
        
        return Particle(px, py, vx, vy, color, size, lifetime,
                       gravity=-100, fade=True, shrink=True)


class SmokeEmitter(ParticleEmitter):
    """Emisor de humo"""
    
    def __init__(self, x, y):
        super().__init__(x, y, emission_rate=10)
        
    def create_particle(self):
        px = self.x + random.uniform(-10, 10)
        py = self.y
        
        vx = random.uniform(-20, 20)
        vy = random.uniform(-40, -20)
        
        gray = random.randint(50, 100)
        color = [gray, gray, gray, 150]
        
        size = random.uniform(5, 10)
        lifetime = random.uniform(1.0, 2.0)
        
        return Particle(px, py, vx, vy, color, size, lifetime,
                       gravity=-20, fade=True, shrink=False)