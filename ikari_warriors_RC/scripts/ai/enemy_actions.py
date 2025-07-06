from scripts.ai.behavior_tree import BehaviorNode, NodeStatus
import math
import random
import pygame

class Explode(BehaviorNode):
    """El kamikaze explota causando daño en área"""
    
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        game = blackboard.get("game")
        
        if not enemy or not game:
            return NodeStatus.FAILURE
            
        # Efectos previos a la explosión
        enemy.flash_color = (255, 0, 0)
        enemy.flash_timer = 0.1
        
        # Crear explosión
        explosion_radius = 100
        explosion_damage = 75
        
        # Solicitar explosión al juego
        blackboard["explosion_request"] = {
            "position": enemy.pos.copy(),
            "radius": explosion_radius,
            "damage": explosion_damage
        }
        
        # Efectos de audio
        if game.audio_manager:
            game.audio_manager.play_sound("kamikaze_scream", 0.8)
        
        # Screen shake
        game.add_screen_shake(15, 0.5)
        
        # Eliminar kamikaze
        enemy.health = 0
        enemy.on_death()
        
        print(f"💥 ¡KAMIKAZE EXPLOTA en {enemy.pos}!")
        
        return NodeStatus.SUCCESS


class PlayChargeSound(BehaviorNode):
    """Reproduce sonido de carga del kamikaze"""
    
    def __init__(self):
        super().__init__("PlayChargeSound")
        self.last_sound_time = 0
        self.sound_cooldown = 1.0
        
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        game = blackboard.get("game")
        current_time = blackboard.get("current_time", 0)
        
        if not enemy or not game:
            return NodeStatus.FAILURE
        
        # Verificar cooldown
        if current_time - self.last_sound_time < self.sound_cooldown:
            return NodeStatus.SUCCESS
            
        # Reproducir sonido si está cerca del jugador
        if enemy.player:
            distance = enemy.pos.distance_to(enemy.player.pos)
            if distance < 300:
                volume = 1.0 - (distance / 300) * 0.5
                if game.audio_manager:
                    game.audio_manager.play_sound("kamikaze_charge", volume)
                self.last_sound_time = current_time
        
        return NodeStatus.SUCCESS


class FlashRed(BehaviorNode):
    """Hace que el enemigo parpadee en rojo (indicador visual)"""
    
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        
        if not enemy:
            return NodeStatus.FAILURE
            
        # Parpadeo más intenso cuando está cerca
        if enemy.player:
            distance = enemy.pos.distance_to(enemy.player.pos)
            if distance < 100:
                # Parpadeo rápido
                enemy.flash_color = (255, 0, 0)
                enemy.flash_timer = 0.1
            elif distance < 200:
                # Parpadeo medio
                enemy.flash_color = (255, 100, 100)
                enemy.flash_timer = 0.2
        
        return NodeStatus.SUCCESS


class LookAround(BehaviorNode):
    """Gira mirando en diferentes direcciones"""
    
    def __init__(self, duration=2.0, rotation_speed=2.0):
        super().__init__("LookAround")
        self.duration = duration
        self.rotation_speed = rotation_speed
        self.start_time = None
        self.initial_angle = None
        
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        current_time = blackboard.get("current_time", 0)
        dt = blackboard.get("dt", 0.016)
        
        if not enemy:
            return NodeStatus.FAILURE
            
        # Inicializar
        if self.start_time is None:
            self.start_time = current_time
            self.initial_angle = enemy.angle
            
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            # Restaurar ángulo inicial
            enemy.angle = self.initial_angle
            self.start_time = None
            self.initial_angle = None
            return NodeStatus.SUCCESS
            
        # Girar suavemente
        rotation = math.sin(elapsed * 2) * self.rotation_speed
        enemy.angle += rotation * dt
        
        # Detener movimiento mientras mira
        enemy.velocity = pygame.math.Vector2(0, 0)
        
        return NodeStatus.RUNNING


class FindHighGround(BehaviorNode):
    """Busca una posición elevada o con buena visibilidad"""
    
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        grid = blackboard.get("grid")
        
        if not enemy or not grid:
            return NodeStatus.FAILURE
            
        # Posiciones estratégicas para francotiradores
        sniper_positions = [
            (100, 100),
            (SCREEN_WIDTH - 100, 100),
            (100, SCREEN_HEIGHT - 100),
            (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
            (SCREEN_WIDTH // 2, 100),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
            (100, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
        ]
        
        # Filtrar posiciones válidas (no ocupadas)
        valid_positions = []
        for pos in sniper_positions:
            node = grid.get_node_from_world_pos(pos[0], pos[1])
            if node and node.walkable:
                # Verificar que no hay otro francotirador cerca
                occupied = False
                for other_enemy in blackboard.get("all_enemies", []):
                    if other_enemy != enemy and other_enemy.enemy_type == "sniper":
                        if math.hypot(pos[0] - other_enemy.pos.x, 
                                    pos[1] - other_enemy.pos.y) < 150:
                            occupied = True
                            break
                
                if not occupied:
                    valid_positions.append(pos)
        
        if not valid_positions:
            return NodeStatus.FAILURE
            
        # Encontrar la posición más cercana con buena línea de visión
        best_pos = None
        best_score = float('inf')
        
        for pos in valid_positions:
            # Calcular score basado en distancia y visibilidad
            dist_to_pos = math.hypot(enemy.pos.x - pos[0], enemy.pos.y - pos[1])
            
            # Bonus si tiene buena vista del centro del mapa
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            dist_to_center = math.hypot(pos[0] - center_x, pos[1] - center_y)
            
            score = dist_to_pos - (dist_to_center * 0.3)  # Preferir posiciones con vista al centro
            
            if score < best_score:
                best_score = score
                best_pos = pos
                
        if best_pos:
            blackboard["sniper_position"] = best_pos
            blackboard["move_to_position"] = best_pos
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE


class MoveToPosition(BehaviorNode):
    """Se mueve a una posición específica"""
    
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        target_pos = blackboard.get("move_to_position")
        pathfinder = blackboard.get("pathfinder")
        
        if not enemy or not target_pos or not pathfinder:
            return NodeStatus.FAILURE
            
        # Verificar si llegamos
        distance = math.hypot(enemy.pos.x - target_pos[0], 
                            enemy.pos.y - target_pos[1])
        
        if distance < 20:
            # Llegamos
            blackboard["move_to_position"] = None
            enemy.velocity = pygame.math.Vector2(0, 0)
            return NodeStatus.SUCCESS
            
        # Actualizar path si es necesario
        if not enemy.path or enemy.path_update_timer >= enemy.path_update_cooldown:
            enemy.path = pathfinder.find_path(
                (enemy.pos.x, enemy.pos.y),
                target_pos
            )
            enemy.path_index = 0
            enemy.path_update_timer = 0
            
        # Seguir path
        if enemy.path:
            enemy.follow_path(blackboard.get("dt", 0.016))
            return NodeStatus.RUNNING
            
        return NodeStatus.FAILURE


class AimAtPlayer(BehaviorNode):
    """Apunta cuidadosamente al jugador (para francotiradores)"""
    
    def __init__(self, aim_time=1.0):
        super().__init__("AimAtPlayer")
        self.aim_time = aim_time
        self.start_time = None
        self.target_angle = None
        
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        current_time = blackboard.get("current_time", 0)
        
        if not enemy or not player:
            return NodeStatus.FAILURE
            
        # Inicializar
        if self.start_time is None:
            self.start_time = current_time
            
            # Calcular ángulo objetivo con predicción
            dx = player.pos.x - enemy.pos.x
            dy = player.pos.y - enemy.pos.y
            distance = math.hypot(dx, dy)
            
            # Predecir posición del jugador
            if hasattr(player, 'velocity') and player.velocity.length() > 0:
                # Tiempo que tarda la bala en llegar
                bullet_time = distance / BULLET_SPEED
                # Posición predicha
                pred_x = player.pos.x + player.velocity.x * bullet_time * 0.5
                pred_y = player.pos.y + player.velocity.y * bullet_time * 0.5
                
                dx = pred_x - enemy.pos.x
                dy = pred_y - enemy.pos.y
            
            self.target_angle = math.atan2(dy, dx)
            
        elapsed = current_time - self.start_time
        
        if elapsed >= self.aim_time:
            # Apuntado completo
            enemy.angle = self.target_angle
            self.start_time = None
            self.target_angle = None
            return NodeStatus.SUCCESS
            
        # Interpolar ángulo suavemente
        progress = elapsed / self.aim_time
        angle_diff = self.target_angle - enemy.angle
        
        # Normalizar diferencia de ángulo
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        enemy.angle += angle_diff * progress * blackboard.get("dt", 0.016) * 5
        
        # Mostrar láser de apuntado
        if enemy.enemy_type == "sniper":
            enemy.show_laser = True
            enemy.laser_alpha = int(progress * 255)
        
        return NodeStatus.RUNNING


class BuffNearbyAllies(BehaviorNode):
    """El oficial mejora a los aliados cercanos"""
    
    def __init__(self, radius=200):
        super().__init__("BuffAllies")
        self.radius = radius
        self.last_buff_time = 0
        self.buff_cooldown = 5.0
        
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        enemies = blackboard.get("all_enemies", [])
        current_time = blackboard.get("current_time", 0)
        game = blackboard.get("game")
        
        if not enemy:
            return NodeStatus.FAILURE
            
        # Verificar cooldown
        if current_time - self.last_buff_time < self.buff_cooldown:
            return NodeStatus.FAILURE
            
        buffed_count = 0
        
        for other_enemy in enemies:
            if other_enemy == enemy or other_enemy.enemy_type == "officer":
                continue
                
            distance = enemy.pos.distance_to(other_enemy.pos)
            
            if distance <= self.radius:
                # Aplicar buffs aleatorios
                buff_type = random.choice(['accuracy', 'speed', 'damage'])
                
                if buff_type == 'accuracy':
                    other_enemy.accuracy_buff = 1.5
                elif buff_type == 'speed':
                    other_enemy.speed_buff = 1.3
                elif buff_type == 'damage':
                    other_enemy.damage_buff = 1.25
                    
                # Efecto visual
                if game:
                    # Línea de buff
                    game.buff_effects.append({
                        'start': enemy.pos.copy(),
                        'end': other_enemy.pos.copy(),
                        'timer': 0.5,
                        'color': (255, 215, 0)
                    })
                    
                buffed_count += 1
                
        if buffed_count > 0:
            self.last_buff_time = current_time
            
            # Animación del oficial
            enemy.flash_color = (255, 215, 0)
            enemy.flash_timer = 0.3
            
            # Sonido
            if game and game.audio_manager:
                game.audio_manager.play_sound("officer_command", 0.7)
            
            print(f"👮 Oficial mejoró a {buffed_count} aliados")
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE


class Flank(BehaviorNode):
    """Intenta flanquear al jugador"""
    
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        player = blackboard.get("player")
        pathfinder = blackboard.get("pathfinder")
        
        if not enemy or not player or not pathfinder:
            return NodeStatus.FAILURE
            
        # Calcular posición de flanqueo
        dx = player.pos.x - enemy.pos.x
        dy = player.pos.y - enemy.pos.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # Normalizar dirección
            dx /= distance
            dy /= distance
            
            # Rotar 90 grados (izquierda o derecha aleatoriamente)
            if random.random() < 0.5:
                # Flanqueo por la izquierda
                flank_dx = -dy
                flank_dy = dx
            else:
                # Flanqueo por la derecha
                flank_dx = dy
                flank_dy = -dx
            
            # Posición objetivo de flanqueo
            flank_distance = 150
            target_x = player.pos.x + flank_dx * flank_distance
            target_y = player.pos.y + flank_dy * flank_distance
            
            # Mantener dentro de la pantalla
            target_x = max(50, min(SCREEN_WIDTH - 50, target_x))
            target_y = max(50, min(SCREEN_HEIGHT - 50, target_y))
            
            blackboard["move_to_position"] = (target_x, target_y)
            
            return NodeStatus.SUCCESS
            
        return NodeStatus.FAILURE


class SteadyAim(BehaviorNode):
    """Mejora la precisión si el enemigo está quieto"""
    
    def __init__(self, steady_time=1.0, accuracy_bonus=0.3):
        super().__init__("SteadyAim")
        self.steady_time = steady_time
        self.accuracy_bonus = accuracy_bonus
        self.start_time = None
        
    def tick(self, blackboard):
        enemy = blackboard.get("enemy")
        current_time = blackboard.get("current_time", 0)
        
        if not enemy:
            return NodeStatus.FAILURE
            
        # Verificar si está quieto
        if enemy.velocity.length() < 10:
            if self.start_time is None:
                self.start_time = current_time
                
            elapsed = current_time - self.start_time
            
            if elapsed >= self.steady_time:
                # Aplicar bonus de precisión
                enemy.accuracy_buff = 1.0 + self.accuracy_bonus
                return NodeStatus.SUCCESS
            else:
                # Mostrar indicador de estabilización
                progress = elapsed / self.steady_time
                enemy.steady_aim_progress = progress
                return NodeStatus.RUNNING
        else:
            # Se movió, resetear
            self.start_time = None
            enemy.accuracy_buff = 1.0
            enemy.steady_aim_progress = 0
            return NodeStatus.FAILURE


# Constantes necesarias
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BULLET_SPEED