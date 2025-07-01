from enum import Enum
from typing import Dict, Any, List, Optional
import random
import math

class NodeStatus(Enum):
    """Estados posibles de un nodo del árbol"""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class BehaviorNode:
    """Clase base para todos los nodos del árbol de comportamiento"""
    
    def __init__(self, name: str = "Node"):
        self.name = name
        self.status = NodeStatus.FAILURE
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        """Ejecuta el nodo y retorna su estado"""
        raise NotImplementedError("tick() debe ser implementado por las subclases")
    
    def reset(self):
        """Reinicia el estado del nodo"""
        self.status = NodeStatus.FAILURE

# Nodos de Control

class Selector(BehaviorNode):
    """
    Nodo Selector (OR): Ejecuta hijos hasta que uno tenga éxito
    Retorna SUCCESS si algún hijo tiene éxito
    Retorna FAILURE si todos los hijos fallan
    """
    
    def __init__(self, name: str = "Selector", children: List[BehaviorNode] = None):
        super().__init__(name)
        self.children = children or []
        self.current_child = 0
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        for i in range(self.current_child, len(self.children)):
            status = self.children[i].tick(blackboard)
            
            if status == NodeStatus.RUNNING:
                self.current_child = i
                return NodeStatus.RUNNING
            elif status == NodeStatus.SUCCESS:
                self.current_child = 0
                return NodeStatus.SUCCESS
                
        self.current_child = 0
        return NodeStatus.FAILURE
    
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset()

class Sequence(BehaviorNode):
    """
    Nodo Sequence (AND): Ejecuta hijos en orden hasta que uno falle
    Retorna SUCCESS si todos los hijos tienen éxito
    Retorna FAILURE si algún hijo falla
    """
    
    def __init__(self, name: str = "Sequence", children: List[BehaviorNode] = None):
        super().__init__(name)
        self.children = children or []
        self.current_child = 0
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        for i in range(self.current_child, len(self.children)):
            status = self.children[i].tick(blackboard)
            
            if status == NodeStatus.RUNNING:
                self.current_child = i
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                self.current_child = 0
                return NodeStatus.FAILURE
                
        self.current_child = 0
        return NodeStatus.SUCCESS
    
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset()

class RandomSelector(BehaviorNode):
    """
    Selector aleatorio: Mezcla y ejecuta hijos como un Selector normal
    Útil para comportamiento impredecible
    """
    
    def __init__(self, name: str = "RandomSelector", children: List[BehaviorNode] = None):
        super().__init__(name)
        self.children = children or []
        self.shuffled_children = []
        self.current_child = 0
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        # Mezclar hijos si es necesario
        if self.current_child == 0:
            self.shuffled_children = self.children.copy()
            random.shuffle(self.shuffled_children)
            
        # Ejecutar como selector normal
        for i in range(self.current_child, len(self.shuffled_children)):
            status = self.shuffled_children[i].tick(blackboard)
            
            if status == NodeStatus.RUNNING:
                self.current_child = i
                return NodeStatus.RUNNING
            elif status == NodeStatus.SUCCESS:
                self.current_child = 0
                return NodeStatus.SUCCESS
                
        self.current_child = 0
        return NodeStatus.FAILURE

class Parallel(BehaviorNode):
    """
    Ejecuta todos los hijos en paralelo
    Requiere un número mínimo de éxitos para retornar SUCCESS
    """
    
    def __init__(self, name: str = "Parallel", children: List[BehaviorNode] = None, 
                 success_threshold: int = 1):
        super().__init__(name)
        self.children = children or []
        self.success_threshold = success_threshold
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        success_count = 0
        failure_count = 0
        running_count = 0
        
        for child in self.children:
            status = child.tick(blackboard)
            
            if status == NodeStatus.SUCCESS:
                success_count += 1
            elif status == NodeStatus.FAILURE:
                failure_count += 1
            else:
                running_count += 1
                
        if success_count >= self.success_threshold:
            return NodeStatus.SUCCESS
        elif running_count > 0:
            return NodeStatus.RUNNING
        else:
            return NodeStatus.FAILURE

# Nodos Decoradores

class Inverter(BehaviorNode):
    """Invierte el resultado del hijo (SUCCESS -> FAILURE, FAILURE -> SUCCESS)"""
    
    def __init__(self, name: str = "Inverter", child: BehaviorNode = None):
        super().__init__(name)
        self.child = child
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        if not self.child:
            return NodeStatus.FAILURE
            
        status = self.child.tick(blackboard)
        
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        elif status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.RUNNING

class Repeater(BehaviorNode):
    """Repite el hijo un número específico de veces o hasta que falle"""
    
    def __init__(self, name: str = "Repeater", child: BehaviorNode = None, 
                 max_loops: int = -1):
        super().__init__(name)
        self.child = child
        self.max_loops = max_loops  # -1 = infinito
        self.current_loop = 0
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        if not self.child:
            return NodeStatus.FAILURE
            
        while self.max_loops < 0 or self.current_loop < self.max_loops:
            status = self.child.tick(blackboard)
            
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                self.current_loop = 0
                return NodeStatus.FAILURE
                
            self.current_loop += 1
            
        self.current_loop = 0
        return NodeStatus.SUCCESS

class Cooldown(BehaviorNode):
    """Limita la frecuencia de ejecución del hijo"""
    
    def __init__(self, name: str = "Cooldown", child: BehaviorNode = None, 
                 cooldown_time: float = 1.0):
        super().__init__(name)
        self.child = child
        self.cooldown_time = cooldown_time
        self.last_execution = -cooldown_time
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        if not self.child:
            return NodeStatus.FAILURE
            
        current_time = blackboard.get("current_time", 0)
        
        if current_time - self.last_execution < self.cooldown_time:
            return NodeStatus.FAILURE
            
        status = self.child.tick(blackboard)
        
        if status != NodeStatus.RUNNING:
            self.last_execution = current_time
            
        return status

# Nodos de Condición (para enemigos)

class IsPlayerVisible(BehaviorNode):
    """Verifica si el jugador es visible"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        
        if not enemy or not player:
            return NodeStatus.FAILURE
            
        distance = enemy.pos.distance_to(player.pos)
        
        if distance <= enemy.sight_range:
            # TODO: Verificar línea de visión con obstáculos
            blackboard["target"] = player
            blackboard["target_distance"] = distance
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class IsPlayerInRange(BehaviorNode):
    """Verifica si el jugador está en rango de ataque"""
    
    def __init__(self, range_type: str = "shoot"):
        super().__init__(f"IsPlayerInRange_{range_type}")
        self.range_type = range_type
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        
        if not enemy or not player:
            return NodeStatus.FAILURE
            
        distance = enemy.pos.distance_to(player.pos)
        
        if self.range_type == "shoot":
            range_value = enemy.shoot_range
        elif self.range_type == "melee":
            range_value = 50  # Rango cuerpo a cuerpo
        else:
            range_value = enemy.sight_range
            
        if distance <= range_value:
            blackboard["target_distance"] = distance
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class HasLowHealth(BehaviorNode):
    """Verifica si el enemigo tiene poca vida"""
    
    def __init__(self, threshold: float = 0.3):
        super().__init__(f"HasLowHealth_{threshold}")
        self.threshold = threshold
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        
        if not enemy:
            return NodeStatus.FAILURE
            
        health_percent = enemy.health / enemy.max_health
        
        if health_percent <= self.threshold:
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class CanShoot(BehaviorNode):
    """Verifica si el enemigo puede disparar"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        
        if not enemy:
            return NodeStatus.FAILURE
            
        if enemy.can_shoot:
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class Random(BehaviorNode):
    """Retorna SUCCESS con cierta probabilidad"""
    
    def __init__(self, probability: float = 0.5):
        super().__init__(f"Random_{probability}")
        self.probability = probability
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        if random.random() < self.probability:
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE

# Nodos de Acción (para enemigos)

class Patrol(BehaviorNode):
    """Patrulla entre puntos predefinidos"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        pathfinder = blackboard.get("pathfinder")
        
        if not enemy or not pathfinder:
            return NodeStatus.FAILURE
            
        # Obtener punto de patrulla actual
        if not hasattr(enemy, "patrol_points") or not enemy.patrol_points:
            return NodeStatus.FAILURE
            
        target_point = enemy.patrol_points[enemy.current_patrol_index]
        
        # Verificar si llegamos
        distance = math.hypot(enemy.pos.x - target_point[0], 
                            enemy.pos.y - target_point[1])
        
        if distance < 20:
            # Siguiente punto
            enemy.current_patrol_index = (enemy.current_patrol_index + 1) % len(enemy.patrol_points)
            return NodeStatus.SUCCESS
            
        # Moverse hacia el punto
        if not enemy.path or enemy.path_update_timer >= enemy.path_update_cooldown:
            enemy.path = pathfinder.find_path(
                (enemy.pos.x, enemy.pos.y),
                target_point
            )
            enemy.path_index = 0
            enemy.path_update_timer = 0
            
        enemy.follow_path(blackboard.get("dt", 0.016))
        return NodeStatus.RUNNING

class ChasePlayer(BehaviorNode):
    """Persigue al jugador"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        pathfinder = blackboard.get("pathfinder")
        
        if not enemy or not player or not pathfinder:
            return NodeStatus.FAILURE
            
        # Actualizar path si es necesario
        if enemy.path_update_timer >= enemy.path_update_cooldown:
            enemy.path = pathfinder.find_path(
                (enemy.pos.x, enemy.pos.y),
                (player.pos.x, player.pos.y)
            )
            enemy.path_index = 0
            enemy.path_update_timer = 0
            
        # Seguir path
        if enemy.path:
            enemy.follow_path(blackboard.get("dt", 0.016))
            return NodeStatus.RUNNING
            
        return NodeStatus.FAILURE

class ShootAtPlayer(BehaviorNode):
    """Dispara al jugador"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        
        if not enemy or not player:
            return NodeStatus.FAILURE
            
        # Apuntar al jugador
        dx = player.pos.x - enemy.pos.x
        dy = player.pos.y - enemy.pos.y
        enemy.angle = math.atan2(dy, dx)
        
        # Disparar
        if enemy.can_shoot:
            enemy.shoot()
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class TakeCover(BehaviorNode):
    """Busca cobertura"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        grid = blackboard.get("grid")
        
        if not enemy or not player or not grid:
            return NodeStatus.FAILURE
            
        # Encontrar obstáculos cercanos
        enemy_node = grid.get_node_from_world_pos(enemy.pos.x, enemy.pos.y)
        if not enemy_node:
            return NodeStatus.FAILURE
            
        # Buscar nodos no caminables cercanos (obstáculos)
        best_cover = None
        best_score = float('inf')
        
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                node = grid.get_node(enemy_node.x + dx, enemy_node.y + dy)
                if not node or not node.walkable:
                    continue
                    
                # Verificar si hay obstáculo adyacente
                has_cover = False
                for ddx, ddy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    adj_node = grid.get_node(node.x + ddx, node.y + ddy)
                    if adj_node and not adj_node.walkable:
                        has_cover = True
                        break
                        
                if has_cover:
                    # Calcular score (distancia al enemigo - distancia al jugador)
                    world_x = node.x * grid.tile_size + grid.tile_size // 2
                    world_y = node.y * grid.tile_size + grid.tile_size // 2
                    
                    dist_to_enemy = math.hypot(world_x - enemy.pos.x, 
                                             world_y - enemy.pos.y)
                    dist_to_player = math.hypot(world_x - player.pos.x, 
                                              world_y - player.pos.y)
                    
                    score = dist_to_enemy - dist_to_player * 0.5
                    
                    if score < best_score:
                        best_score = score
                        best_cover = (world_x, world_y)
                        
        if best_cover:
            blackboard["cover_position"] = best_cover
            # Moverse hacia la cobertura
            # TODO: Implementar movimiento
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class CallReinforcements(BehaviorNode):
    """Llama refuerzos"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        game = blackboard.get("game")
        
        if not enemy or not game:
            return NodeStatus.FAILURE
            
        # Marcar que se necesitan refuerzos
        blackboard["reinforcements_called"] = True
        blackboard["reinforcements_position"] = (enemy.pos.x, enemy.pos.y)
        
        # TODO: Implementar spawn de refuerzos en Game
        print(f"¡{enemy.enemy_type} pidiendo refuerzos!")
        
        return NodeStatus.SUCCESS

class Retreat(BehaviorNode):
    """Retrocede del jugador"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        
        if not enemy or not player:
            return NodeStatus.FAILURE
            
        # Calcular dirección opuesta al jugador
        dx = enemy.pos.x - player.pos.x
        dy = enemy.pos.y - player.pos.y
        
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
            
            # Mover en dirección opuesta
            enemy.velocity.x = dx * enemy.speed * 0.8
            enemy.velocity.y = dy * enemy.speed * 0.8
            
            return NodeStatus.RUNNING
            
        return NodeStatus.FAILURE

# Clase para manejar el árbol completo

class BehaviorTree:
    """Maneja un árbol de comportamiento completo"""
    
    def __init__(self, root: BehaviorNode):
        self.root = root
        self.blackboard = {}
        
    def tick(self, blackboard_updates: Dict[str, Any] = None) -> NodeStatus:
        """Ejecuta el árbol con el blackboard actualizado"""
        if blackboard_updates:
            self.blackboard.update(blackboard_updates)
            
        return self.root.tick(self.blackboard)
    
    def reset(self):
        """Reinicia el árbol"""
        self.root.reset()
        
    def set_blackboard(self, key: str, value: Any):
        """Establece un valor en el blackboard"""
        self.blackboard[key] = value
        
    def get_blackboard(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor del blackboard"""
        return self.blackboard.get(key, default)