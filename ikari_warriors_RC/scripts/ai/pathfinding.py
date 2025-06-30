import math
from typing import List, Tuple, Optional, Set
import pygame

class Node:
    """Representa un nodo en el grid para A*"""
    
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x
        self.y = y
        self.walkable = walkable
        
        # Valores para A*
        self.g_cost = float('inf')  # Costo desde el inicio
        self.h_cost = 0  # Heurística (distancia estimada al objetivo)
        self.f_cost = float('inf')  # g + h
        
        self.parent = None  # Nodo padre para reconstruir el camino
        
    def reset(self):
        """Reinicia los valores del nodo para un nuevo pathfinding"""
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = float('inf')
        self.parent = None
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other):
        """Para comparación en la cola de prioridad"""
        return self.f_cost < other.f_cost
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Node({self.x}, {self.y})"

class Grid:
    """Representa el grid del mundo para pathfinding"""
    
    def __init__(self, width: int, height: int, tile_size: int):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Crear grid de nodos
        self.nodes = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(Node(x, y))
            self.nodes.append(row)
            
    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Obtiene un nodo en las coordenadas dadas"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.nodes[y][x]
        return None
    
    def get_node_from_world_pos(self, world_x: float, world_y: float) -> Optional[Node]:
        """Convierte coordenadas del mundo a nodo del grid"""
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return self.get_node(grid_x, grid_y)
    
    def set_walkable(self, x: int, y: int, walkable: bool):
        """Establece si un nodo es caminable o no"""
        node = self.get_node(x, y)
        if node:
            node.walkable = walkable
    
    def reset_nodes(self):
        """Reinicia todos los nodos para un nuevo pathfinding"""
        for row in self.nodes:
            for node in row:
                node.reset()
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """Obtiene los vecinos caminables de un nodo"""
        neighbors = []
        
        # 8 direcciones (incluye diagonales)
        directions = [
            (-1, -1), (0, -1), (1, -1),  # Arriba
            (-1, 0),           (1, 0),    # Lados
            (-1, 1),  (0, 1),  (1, 1)     # Abajo
        ]
        
        for dx, dy in directions:
            x, y = node.x + dx, node.y + dy
            neighbor = self.get_node(x, y)
            
            if neighbor and neighbor.walkable:
                # Verificar que las diagonales sean accesibles
                if dx != 0 and dy != 0:  # Es diagonal
                    # Verificar que los dos lados estén libres
                    side1 = self.get_node(node.x + dx, node.y)
                    side2 = self.get_node(node.x, node.y + dy)
                    
                    if side1 and side2 and side1.walkable and side2.walkable:
                        neighbors.append(neighbor)
                else:
                    neighbors.append(neighbor)
                    
        return neighbors
    
    def get_distance(self, node_a: Node, node_b: Node) -> float:
        """Calcula la distancia entre dos nodos"""
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        
        # Distancia diagonal = 1.414 (√2), distancia recta = 1
        if dx > dy:
            return 1.414 * dy + (dx - dy)
        return 1.414 * dx + (dy - dx)

class AStar:
    """Implementación del algoritmo A*"""
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.path_cache = {}  # Cache para rutas calculadas
        
    def find_path(self, start_pos: Tuple[float, float], 
                  end_pos: Tuple[float, float]) -> List[Tuple[int, int]]:
        """
        Encuentra el camino más corto entre dos posiciones del mundo
        Retorna una lista de coordenadas de grid (x, y)
        """
        # Reiniciar nodos
        self.grid.reset_nodes()
        
        # Convertir posiciones del mundo a nodos del grid
        start_node = self.grid.get_node_from_world_pos(start_pos[0], start_pos[1])
        end_node = self.grid.get_node_from_world_pos(end_pos[0], end_pos[1])
        
        if not start_node or not end_node:
            print(f"Nodos inválidos: start={start_node}, end={end_node}")
            return []
            
        if not end_node.walkable:
            print(f"Nodo destino no es caminable: {end_node}")
            return []
        
        # Verificar cache
        cache_key = (start_node.x, start_node.y, end_node.x, end_node.y)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        # Listas para A*
        open_set = [start_node]
        closed_set = set()
        
        # Inicializar nodo inicial
        start_node.g_cost = 0
        start_node.h_cost = self._heuristic(start_node, end_node)
        start_node.f_cost = start_node.h_cost
        
        nodes_explored = 0
        
        while open_set:
            # Obtener nodo con menor f_cost
            current = min(open_set, key=lambda n: n.f_cost)
            open_set.remove(current)
            closed_set.add(current)
            
            nodes_explored += 1
            
            # Si llegamos al objetivo, reconstruir camino
            if current == end_node:
                path = self._reconstruct_path(current)
                self.path_cache[cache_key] = path
                print(f"Path encontrado! Nodos explorados: {nodes_explored}")
                return path
            
            # Explorar vecinos
            for neighbor in self.grid.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Calcular nuevo g_cost
                tentative_g = current.g_cost + self.grid.get_distance(current, neighbor)
                
                # Si encontramos un mejor camino al vecino
                if tentative_g < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g
                    neighbor.h_cost = self._heuristic(neighbor, end_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        
        # No se encontró camino
        print(f"No se encontró path. Nodos explorados: {nodes_explored}")
        return []
    
    def _heuristic(self, node_a: Node, node_b: Node) -> float:
        """Función heurística - Distancia de Manhattan con diagonales"""
        return self.grid.get_distance(node_a, node_b)
    
    def _reconstruct_path(self, end_node: Node) -> List[Tuple[int, int]]:
        """Reconstruye el camino desde el nodo final"""
        path = []
        current = end_node
        
        while current:
            path.append((current.x, current.y))
            current = current.parent
            
        path.reverse()
        return path
    
    def clear_cache(self):
        """Limpia el cache de rutas"""
        self.path_cache.clear()
    
    def draw_path(self, screen: pygame.Surface, path: List[Tuple[int, int]], 
                  color: Tuple[int, int, int] = (255, 255, 0)):
        """Dibuja el camino en pantalla (útil para debug)"""
        if len(path) < 2:
            return
            
        # Convertir coordenadas de grid a mundo
        world_points = []
        for x, y in path:
            world_x = x * self.grid.tile_size + self.grid.tile_size // 2
            world_y = y * self.grid.tile_size + self.grid.tile_size // 2
            world_points.append((world_x, world_y))
        
        # Dibujar línea
        pygame.draw.lines(screen, color, False, world_points, 3)
        
        # Dibujar puntos
        for point in world_points:
            pygame.draw.circle(screen, color, point, 5)