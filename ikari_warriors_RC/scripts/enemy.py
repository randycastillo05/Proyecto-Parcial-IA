"""
Randy Castillo
Módulo de Enemigos con IA
Contiene la clase Enemy con Árbol de Comportamiento y A*
"""

import pygame
import math
import random
import os
from collections import deque
from enum import Enum

# Constantes
ENEMY_SIZE = 32
ENEMY_SPEED = 2
SHOOT_RANGE = 200
DETECTION_RANGE = 300

# Colores
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

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
        surface.fill(color_fallback or RED)
        return surface
    return None

class NodeStatus(Enum):
    """Estados de los nodos del árbol de comportamiento"""
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3

class BehaviorNode:
    """Nodo base del árbol de comportamiento"""
    def execute(self, enemy):
        raise NotImplementedError

class SequenceNode(BehaviorNode):
    """Nodo secuencia - ejecuta hijos en orden hasta que uno falle"""
    def __init__(self, children):
        self.children = children
    
    def execute(self, enemy):
        for child in self.children:
            status = child.execute(enemy)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS

class SelectorNode(BehaviorNode):
    """Nodo selector - ejecuta hijos hasta que uno tenga éxito"""
    def __init__(self, children):
        self.children = children
    
    def execute(self, enemy):
        for child in self.children:
            status = child.execute(enemy)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE

class ConditionNode(BehaviorNode):
    """Nodo condición - verifica una condición"""
    def __init__(self, condition_func):
        self.condition_func = condition_func
    
    def execute(self, enemy):
        if self.condition_func(enemy):
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE

class ActionNode(BehaviorNode):
    """Nodo acción - ejecuta una acción"""
    def __init__(self, action_func):
        self.action_func = action_func
    
    def execute(self, enemy):
        return self.action_func(enemy)

class EnemyBullet(pygame.sprite.Sprite):
    """Bala del enemigo"""
    def __init__(self, x, y, direction):
        super().__init__()
        
        # Cargar sprite de bala enemiga
        self.image = load_sprite("assets/images/enemy_bullet.png", (8, 8), YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 6
        self.direction = direction
        
    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        if (self.rect.bottom < 0 or self.rect.top > 600 or 
            self.rect.right < 0 or self.rect.left > 800):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """Clase enemigo con IA"""
    def __init__(self, x, y):
        super().__init__()
        
        # Cargar sprites del enemigo
        self.sprites = {
            'idle': load_sprite("assets/images/enemy.png", (ENEMY_SIZE, ENEMY_SIZE), RED),
            'alert': load_sprite("assets/images/enemy_alert.png", (ENEMY_SIZE, ENEMY_SIZE), RED)
        }
        
        # Si no hay sprite de alerta, usar el mismo
        if not os.path.exists("assets/images/enemy_alert.png"):
            self.sprites['alert'] = self.sprites['idle']
        
        # Sprite inicial
        self.image = self.sprites['idle']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Atributos
        self.speed = ENEMY_SPEED
        self.target = None
        self.walls = None
        self.shoot_cooldown = 0
        self.path = []
        self.path_index = 0
        self.last_path_update = 0
        self.is_alert = False
        
        # Construir árbol de comportamiento
        self.behavior_tree = self._build_behavior_tree()
        
    def _build_behavior_tree(self):
        """Construye el árbol de comportamiento"""
        # Condiciones
        can_see_player = ConditionNode(lambda e: e._can_see_player())
        is_in_shoot_range = ConditionNode(lambda e: e._is_in_shoot_range())
        has_path = ConditionNode(lambda e: len(e.path) > 0)
        
        # Acciones
        shoot_action = ActionNode(lambda e: e._shoot_at_player())
        move_to_player = ActionNode(lambda e: e._move_towards_player())
        patrol_action = ActionNode(lambda e: e._patrol())
        
        # Secuencia de ataque
        attack_sequence = SequenceNode([
            can_see_player,
            is_in_shoot_range,
            shoot_action
        ])
        
        # Secuencia de persecución
        chase_sequence = SequenceNode([
            can_see_player,
            move_to_player
        ])
        
        # Selector principal
        root = SelectorNode([
            attack_sequence,
            chase_sequence,
            patrol_action
        ])
        
        return root
    
    def set_target(self, target):
        """Establece el objetivo (jugador)"""
        self.target = target
        
    def set_walls(self, walls):
        """Establece las paredes para pathfinding"""
        self.walls = walls
    
    def _can_see_player(self):
        """Verifica si puede ver al jugador"""
        if not self.target:
            return False
            
        # Distancia al jugador
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        can_see = distance <= DETECTION_RANGE
        
        # Cambiar sprite si puede ver al jugador
        if can_see != self.is_alert:
            self.is_alert = can_see
            self.image = self.sprites['alert'] if can_see else self.sprites['idle']
        
        return can_see
    
    def _is_in_shoot_range(self):
        """Verifica si está en rango de disparo"""
        if not self.target:
            return False
            
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        return distance <= SHOOT_RANGE
    
    def _shoot_at_player(self):
        """Dispara al jugador"""
        if self.shoot_cooldown <= 0 and self.target:
            self.shoot_cooldown = 30
            
            # Calcular dirección
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                direction = (dx/distance, dy/distance)
                self.last_bullet = EnemyBullet(self.rect.centerx, self.rect.centery, direction)
                return NodeStatus.SUCCESS
                
        return NodeStatus.FAILURE
    
    def _move_towards_player(self):
        """Se mueve hacia el jugador usando A*"""
        if not self.target:
            return NodeStatus.FAILURE
        
        # Actualizar path cada 30 frames
        if self.last_path_update <= 0:
            self.path = self._find_path_astar()
            self.path_index = 0
            self.last_path_update = 30
        
        # Seguir el path
        if self.path and self.path_index < len(self.path):
            next_pos = self.path[self.path_index]
            
            # Mover hacia el siguiente punto
            dx = next_pos[0] - self.rect.centerx
            dy = next_pos[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 5:
                # Normalizar y mover
                self.rect.x += (dx/distance) * self.speed
                self.rect.y += (dy/distance) * self.speed
            else:
                # Llegamos al punto, siguiente
                self.path_index += 1
                
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE
    
    def _patrol(self):
        """Patrulla aleatoriamente"""
        # Movimiento aleatorio simple
        if random.randint(0, 30) == 0:
            self.rect.x += random.choice([-1, 0, 1]) * self.speed
            self.rect.y += random.choice([-1, 0, 1]) * self.speed
            
        # Mantener en pantalla
        self.rect.x = max(0, min(780, self.rect.x))
        self.rect.y = max(0, min(580, self.rect.y))
        
        return NodeStatus.SUCCESS
    
    def _find_path_astar(self):
        """Implementación simple de A* para pathfinding"""
        if not self.target:
            return []
        
        # Convertir posiciones a grid
        grid_size = 40
        start = (self.rect.centerx // grid_size, self.rect.centery // grid_size)
        goal = (self.target.rect.centerx // grid_size, self.target.rect.centery // grid_size)
        
        # A* simplificado
        open_set = [(start, 0)]
        came_from = {}
        g_score = {start: 0}
        
        while open_set:
            current, _ = min(open_set, key=lambda x: x[1])
            open_set.remove((current, _))
            
            if current == goal:
                # Reconstruir path
                path = []
                while current in came_from:
                    path.append((current[0] * grid_size, current[1] * grid_size))
                    current = came_from[current]
                return path[::-1]
            
            # Explorar vecinos
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Verificar límites
                if (neighbor[0] < 0 or neighbor[0] > 20 or 
                    neighbor[1] < 0 or neighbor[1] > 15):
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                    open_set.append((neighbor, f_score))
        
        return []
    
    def think_and_act(self):
        """Ejecuta el árbol de comportamiento"""
        self.behavior_tree.execute(self)
        
        # Actualizar cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.last_path_update > 0:
            self.last_path_update -= 1
        
        # Retornar bala si se disparó
        if hasattr(self, 'last_bullet'):
            bullet = self.last_bullet
            delattr(self, 'last_bullet')
            return bullet
        
        return None
    
    def update(self):
        """Actualiza el enemigo"""
        pass  # La lógica está en think_and_act