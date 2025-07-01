from scripts.ai.behavior_tree import *
from scripts.utils.constants import EnemyType, SCREEN_WIDTH, SCREEN_HEIGHT

class EnemyBehaviorFactory:
    """Factory para crear árboles de comportamiento según el tipo de enemigo"""
    
    @staticmethod
    def create_soldier_tree() -> BehaviorTree:
        """
        Soldado básico: Patrulla, persigue y dispara
        Comportamiento simple pero efectivo
        """
        root = Selector(name="SoldierRoot", children=[
            # Prioridad 1: Combate
            Sequence(name="Combat", children=[
                IsPlayerVisible(),
                Selector(name="CombatOptions", children=[
                    # Si está en rango de disparo
                    Sequence(name="AttackSequence", children=[
                        IsPlayerInRange("shoot"),
                        CanShoot(),
                        ShootAtPlayer()
                    ]),
                    # Si no, perseguir
                    ChasePlayer()
                ])
            ]),
            
            # Prioridad 2: Patrulla
            Patrol()
        ])
        
        return BehaviorTree(root)
    
    @staticmethod
    def create_elite_tree() -> BehaviorTree:
        """
        Soldado élite: Más táctico, usa cobertura, mejor puntería
        """
        root = Selector(name="EliteRoot", children=[
            # Prioridad 1: Supervivencia
            Sequence(name="Survival", children=[
                HasLowHealth(0.4),
                Selector(name="SurvivalOptions", children=[
                    TakeCover(),
                    Retreat()
                ])
            ]),
            
            # Prioridad 2: Combate táctico
            Sequence(name="TacticalCombat", children=[
                IsPlayerVisible(),
                Selector(name="TacticalOptions", children=[
                    # Disparar desde cobertura
                    Sequence(name="CoverFire", children=[
                        IsPlayerInRange("shoot"),
                        CanShoot(),
                        Random(0.7),  # No siempre dispara, más realista
                        ShootAtPlayer()
                    ]),
                    # Flanquear al jugador
                    Sequence(name="Flank", children=[
                        Random(0.3),  # 30% de intentar flanquear
                        ChasePlayer()  # TODO: Implementar movimiento de flanqueo
                    ]),
                    # Persecución normal
                    ChasePlayer()
                ])
            ]),
            
            # Prioridad 3: Patrulla alerta
            Sequence(name="AlertPatrol", children=[
                Patrol(),
                Random(0.1),  # 10% de mirar alrededor
                # TODO: Implementar LookAround
            ])
        ])
        
        return BehaviorTree(root)
    
    @staticmethod
    def create_sniper_tree() -> BehaviorTree:
        """
        Francotirador: Mantiene distancia, alta precisión, vulnerable cerca
        """
        root = Selector(name="SniperRoot", children=[
            # Prioridad 1: Mantener distancia
            Sequence(name="KeepDistance", children=[
                IsPlayerInRange("melee"),  # Muy cerca
                Retreat()
            ]),
            
            # Prioridad 2: Disparo de precisión
            Sequence(name="PrecisionShot", children=[
                IsPlayerVisible(),
                Selector(name="SniperOptions", children=[
                    # Disparo perfecto si está quieto
                    Sequence(name="SteadyShot", children=[
                        IsPlayerInRange("shoot"),
                        Cooldown(name="AimTime", child=ShootAtPlayer(), cooldown_time=1.5)
                    ]),
                    # Reposicionarse para mejor ángulo
                    Sequence(name="Reposition", children=[
                        Random(0.4),
                        TakeCover()
                    ])
                ])
            ]),
            
            # Prioridad 3: Buscar posición de francotirador
            Sequence(name="FindSniperSpot", children=[
                TakeCover(),
                # TODO: Implementar FindHighGround
            ])
        ])
        
        return BehaviorTree(root)
    
    @staticmethod
    def create_kamikaze_tree() -> BehaviorTree:
        """
        Kamikaze: Corre hacia el jugador para explotar
        Rápido, agresivo, peligroso de cerca
        """
        root = Selector(name="KamikazeRoot", children=[
            # Prioridad 1: Explotar si está cerca
            Sequence(name="Explode", children=[
                IsPlayerInRange("melee"),
                # TODO: Implementar Explode action
            ]),
            
            # Prioridad 2: Cargar hacia el jugador
            Sequence(name="ChargePlayer", children=[
                IsPlayerVisible(),
                Parallel(name="AggressiveCharge", children=[
                    ChasePlayer(),
                    # TODO: Implementar PlayChargeSound
                    # TODO: Implementar FlashRed (indicador visual)
                ], success_threshold=1)
            ]),
            
            # Prioridad 3: Búsqueda activa
            RandomSelector(name="ActiveSearch", children=[
                Patrol(),
                # TODO: Implementar MoveToLastKnownPosition
            ])
        ])
        
        return BehaviorTree(root)
    
    @staticmethod
    def create_officer_tree() -> BehaviorTree:
        """
        Oficial: Llama refuerzos, buff a aliados, combate defensivo
        """
        root = Selector(name="OfficerRoot", children=[
            # Prioridad 1: Llamar refuerzos si es necesario
            Sequence(name="CallBackup", children=[
                IsPlayerVisible(),
                Inverter(child=Random(0.7)),  # 30% chance
                Cooldown(name="ReinforceCooldown", 
                        child=CallReinforcements(), 
                        cooldown_time=10.0)
            ]),
            
            # Prioridad 2: Combate defensivo
            Sequence(name="DefensiveCombat", children=[
                IsPlayerVisible(),
                Parallel(name="CombatActions", children=[
                    # Disparar mientras retrocede
                    Sequence(name="ShootAndMove", children=[
                        IsPlayerInRange("shoot"),
                        CanShoot(),
                        ShootAtPlayer()
                    ]),
                    # Mantener distancia media
                    Sequence(name="MaintainDistance", children=[
                        IsPlayerInRange("melee"),
                        Retreat()
                    ])
                ], success_threshold=1)
            ]),
            
            # Prioridad 3: Patrulla y coordinar
            Sequence(name="CoordinatePatrol", children=[
                Patrol(),
                # TODO: Implementar BuffNearbyAllies
            ])
        ])
        
        return BehaviorTree(root)
    
    @staticmethod
    def create_behavior_tree(enemy_type: str) -> BehaviorTree:
        """Crea el árbol apropiado según el tipo de enemigo"""
        if enemy_type == EnemyType.SOLDIER:
            return EnemyBehaviorFactory.create_soldier_tree()
        elif enemy_type == EnemyType.ELITE:
            return EnemyBehaviorFactory.create_elite_tree()
        elif enemy_type == EnemyType.SNIPER:
            return EnemyBehaviorFactory.create_sniper_tree()
        elif enemy_type == EnemyType.KAMIKAZE:
            return EnemyBehaviorFactory.create_kamikaze_tree()
        elif enemy_type == EnemyType.OFFICER:
            return EnemyBehaviorFactory.create_officer_tree()
        else:
            # Default: comportamiento de soldado
            return EnemyBehaviorFactory.create_soldier_tree()

# Nodos de acción adicionales específicos

class Explode(BehaviorNode):
    """El kamikaze explota causando daño en área"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        game = blackboard.get("game")
        
        if not enemy or not game:
            return NodeStatus.FAILURE
            
        # Crear explosión
        explosion_radius = 100
        explosion_damage = 75
        
        # TODO: Implementar en game.create_explosion()
        blackboard["explosion_request"] = {
            "position": (enemy.pos.x, enemy.pos.y),
            "radius": explosion_radius,
            "damage": explosion_damage
        }
        
        # Eliminar kamikaze
        enemy.health = 0
        print(f"¡KAMIKAZE EXPLOTA en {enemy.pos}!")
        
        return NodeStatus.SUCCESS

class BuffNearbyAllies(BehaviorNode):
    """El oficial mejora a los aliados cercanos"""
    
    def __init__(self, radius: float = 200, buff_type: str = "accuracy"):
        super().__init__(f"BuffAllies_{buff_type}")
        self.radius = radius
        self.buff_type = buff_type
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        enemies = blackboard.get("all_enemies", [])
        
        if not enemy:
            return NodeStatus.FAILURE
            
        buffed_count = 0
        
        for other_enemy in enemies:
            if other_enemy == enemy:
                continue
                
            distance = enemy.pos.distance_to(other_enemy.pos)
            
            if distance <= self.radius:
                # Aplicar buff
                if self.buff_type == "accuracy":
                    other_enemy.accuracy_buff = 1.5
                elif self.buff_type == "speed":
                    other_enemy.speed_buff = 1.3
                elif self.buff_type == "damage":
                    other_enemy.damage_buff = 1.25
                    
                buffed_count += 1
                
        if buffed_count > 0:
            print(f"Oficial buffed {buffed_count} aliados con {self.buff_type}")
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE

class MoveToLastKnownPosition(BehaviorNode):
    """Se mueve a la última posición conocida del jugador"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        last_known_pos = blackboard.get("last_player_position")
        pathfinder = blackboard.get("pathfinder")
        
        if not enemy or not last_known_pos or not pathfinder:
            return NodeStatus.FAILURE
            
        # Verificar si llegamos
        distance = math.hypot(enemy.pos.x - last_known_pos[0], 
                            enemy.pos.y - last_known_pos[1])
        
        if distance < 30:
            # Llegamos, olvidar posición
            blackboard["last_player_position"] = None
            return NodeStatus.SUCCESS
            
        # Moverse hacia la posición
        if not enemy.path or enemy.path_update_timer >= enemy.path_update_cooldown:
            enemy.path = pathfinder.find_path(
                (enemy.pos.x, enemy.pos.y),
                last_known_pos
            )
            enemy.path_index = 0
            enemy.path_update_timer = 0
            
        enemy.follow_path(blackboard.get("dt", 0.016))
        return NodeStatus.RUNNING

class LookAround(BehaviorNode):
    """Gira mirando en diferentes direcciones"""
    
    def __init__(self, duration: float = 2.0):
        super().__init__("LookAround")
        self.duration = duration
        self.start_time = None
        
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        current_time = blackboard.get("current_time", 0)
        
        if not enemy:
            return NodeStatus.FAILURE
            
        if self.start_time is None:
            self.start_time = current_time
            
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.start_time = None
            return NodeStatus.SUCCESS
            
        # Girar
        enemy.angle += 2.0 * blackboard.get("dt", 0.016)
        
        return NodeStatus.RUNNING

class FlashRed(BehaviorNode):
    """Hace que el enemigo parpadee en rojo (indicador visual)"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        
        if not enemy:
            return NodeStatus.FAILURE
            
        enemy.flash_color = (255, 0, 0)
        enemy.flash_timer = 0.1
        
        return NodeStatus.SUCCESS

class FindHighGround(BehaviorNode):
    """Busca una posición elevada o con buena visibilidad"""
    
    def tick(self, blackboard: Dict[str, Any]) -> NodeStatus:
        enemy = blackboard.get("enemy")
        grid = blackboard.get("grid")
        
        if not enemy or not grid:
            return NodeStatus.FAILURE
            
        # Por ahora, buscar esquinas del mapa (simulando posiciones elevadas)
        sniper_positions = [
            (100, 100),
            (SCREEN_WIDTH - 100, 100),
            (100, SCREEN_HEIGHT - 100),
            (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        ]
        
        # Encontrar la posición más cercana
        best_pos = None
        best_dist = float('inf')
        
        for pos in sniper_positions:
            dist = math.hypot(enemy.pos.x - pos[0], enemy.pos.y - pos[1])
            if dist < best_dist:
                best_dist = dist
                best_pos = pos
                
        if best_pos:
            blackboard["sniper_position"] = best_pos
            # TODO: Moverse hacia esa posición
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE