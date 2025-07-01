from scripts.ai.behavior_tree import *
from scripts.utils.constants import EnemyType

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
                    return distance