import json
import os
import time
import math

class ProgressionSystem:
    """Sistema de progresión del jugador"""
    
    def __init__(self):
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.skill_points = 0
        
        # Stats del jugador
        self.stats = {
            'max_health': 100,
            'damage_multiplier': 1.0,
            'fire_rate': 1.0,
            'movement_speed': 1.0,
            'critical_chance': 0.05,
            'critical_damage': 2.0,
            'health_regen': 0,
            'dodge_chance': 0
        }
        
        # Habilidades desbloqueables
        self.skills = {
            'rapid_fire': {'unlocked': False, 'level': 0, 'max_level': 5},
            'explosive_rounds': {'unlocked': False, 'level': 0, 'max_level': 3},
            'dash': {'unlocked': False, 'level': 0, 'max_level': 3},
            'shield': {'unlocked': False, 'level': 0, 'max_level': 5},
            'lifesteal': {'unlocked': False, 'level': 0, 'max_level': 3},
            'multi_shot': {'unlocked': False, 'level': 0, 'max_level': 5}
        }
        
        # Logros
        self.achievements = {
            'first_blood': {'unlocked': False, 'description': 'Elimina tu primer enemigo'},
            'survivor': {'unlocked': False, 'description': 'Sobrevive 10 oleadas'},
            'untouchable': {'unlocked': False, 'description': 'Completa una oleada sin recibir daño'},
            'combo_master': {'unlocked': False, 'description': 'Alcanza un combo x10'},
            'speed_demon': {'unlocked': False, 'description': 'Elimina 5 enemigos en 5 segundos'},
            'elite_hunter': {'unlocked': False, 'description': 'Elimina 50 enemigos élite'},
            'kamikaze_dodger': {'unlocked': False, 'description': 'Esquiva 10 kamikazes'},
            'sharpshooter': {'unlocked': False, 'description': '95% precisión en una oleada'},
            'millionaire': {'unlocked': False, 'description': 'Acumula 1,000,000 puntos'},
            'perfectionist': {'unlocked': False, 'description': 'Completa 5 oleadas perfectas'}
        }
        
        # Estadísticas de juego
        self.statistics = {
            'enemies_killed': 0,
            'shots_fired': 0,
            'shots_hit': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'waves_completed': 0,
            'highest_combo': 0,
            'time_played': 0,
            'power_ups_collected': 0,
            'deaths': 0
        }
        
        # Desafíos diarios
        self.daily_challenges = self.generate_daily_challenges()
        
    def add_experience(self, amount):
        """Añade experiencia y maneja subida de nivel"""
        self.experience += amount
        
        level_ups = 0
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            level_ups += 1
            self.skill_points += 2  # 2 puntos por nivel
            
            # Aumentar requisito de experiencia
            self.experience_to_next_level = int(100 * math.pow(1.5, self.level - 1))
            
            # Bonus de stats por nivel
            self.stats['max_health'] += 10
            self.stats['damage_multiplier'] += 0.05
            
        return level_ups
    
    def unlock_skill(self, skill_name):
        """Desbloquea o mejora una habilidad"""
        if skill_name in self.skills and self.skill_points > 0:
            skill = self.skills[skill_name]
            
            if not skill['unlocked']:
                skill['unlocked'] = True
                skill['level'] = 1
                self.skill_points -= 1
                return True
            elif skill['level'] < skill['max_level']:
                skill['level'] += 1
                self.skill_points -= 1
                return True
                
        return False
    
    def check_achievement(self, achievement_id, condition):
        """Verifica y desbloquea logros"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]['unlocked']:
            if condition:
                self.achievements[achievement_id]['unlocked'] = True
                return achievement_id
        return None
    
    def generate_daily_challenges(self):
        """Genera desafíos diarios"""
        import random
        from datetime import datetime
        
        # Usar la fecha como semilla para que sean consistentes durante el día
        today = datetime.now().strftime("%Y%m%d")
        random.seed(int(today))
        
        challenge_templates = [
            {'type': 'kills', 'target': random.randint(50, 150), 'reward': 500},
            {'type': 'accuracy', 'target': random.randint(70, 90), 'reward': 300},
            {'type': 'no_damage_waves', 'target': random.randint(2, 5), 'reward': 1000},
            {'type': 'combo', 'target': random.randint(15, 25), 'reward': 400},
            {'type': 'specific_enemy', 'enemy': random.choice(['elite', 'sniper', 'officer']), 
             'target': random.randint(10, 30), 'reward': 600}
        ]
        
        # Seleccionar 3 desafíos aleatorios
        daily = random.sample(challenge_templates, 3)
        
        # Resetear semilla
        random.seed()
        
        return daily
    
    def get_skill_description(self, skill_name):
        """Obtiene la descripción de una habilidad"""
        descriptions = {
            'rapid_fire': f"Aumenta la velocidad de disparo en {20 * self.skills['rapid_fire']['level']}%",
            'explosive_rounds': f"Las balas tienen {10 * self.skills['explosive_rounds']['level']}% de causar explosión",
            'dash': f"Dash con {self.skills['dash']['level']} cargas. Cooldown: {5 - self.skills['dash']['level']}s",
            'shield': f"Escudo de {50 * self.skills['shield']['level']} puntos. Se regenera cada 30s",
            'lifesteal': f"Recupera {5 * self.skills['lifesteal']['level']}% del daño infligido como vida",
            'multi_shot': f"Dispara {1 + self.skills['multi_shot']['level']} proyectiles"
        }
        
        return descriptions.get(skill_name, "")
    
    def save_progress(self, filename="save_game.json"):
        """Guarda el progreso del jugador"""
        save_data = {
            'level': self.level,
            'experience': self.experience,
            'skill_points': self.skill_points,
            'stats': self.stats,
            'skills': self.skills,
            'achievements': self.achievements,
            'statistics': self.statistics,
            'timestamp': time.time()
        }
        
        save_path = os.path.join("saves", filename)
        os.makedirs("saves", exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
            
        return True
    
    def load_progress(self, filename="save_game.json"):
        """Carga el progreso del jugador"""
        save_path = os.path.join("saves", filename)
        
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                save_data = json.load(f)
                
            self.level = save_data.get('level', 1)
            self.experience = save_data.get('experience', 0)
            self.skill_points = save_data.get('skill_points', 0)
            self.stats.update(save_data.get('stats', {}))
            self.skills.update(save_data.get('skills', {}))
            self.achievements.update(save_data.get('achievements', {}))
            self.statistics.update(save_data.get('statistics', {}))
            
            return True
            
        return False


class ComboSystem:
    """Sistema de combos para hacer el combate más dinámico"""
    
    def __init__(self):
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 2.0  # Segundos para mantener el combo
        self.combo_multiplier = 1.0
        
        # Hitos de combo
        self.combo_milestones = {
            5: {'multiplier': 1.5, 'effect': 'speed_boost'},
            10: {'multiplier': 2.0, 'effect': 'damage_boost'},
            15: {'multiplier': 2.5, 'effect': 'invincibility'},
            25: {'multiplier': 3.0, 'effect': 'explosive_rounds'},
            50: {'multiplier': 5.0, 'effect': 'god_mode'}
        }
        
        # Estado actual de efectos
        self.active_effects = set()
        
    def add_kill(self):
        """Añade una eliminación al combo"""
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        
        # Verificar hitos
        for milestone, rewards in self.combo_milestones.items():
            if self.combo_count == milestone:
                self.combo_multiplier = rewards['multiplier']
                self.active_effects.add(rewards['effect'])
                return rewards['effect']
                
        return None
    
    def update(self, dt):
        """Actualiza el sistema de combos"""
        if self.combo_timer > 0:
            self.combo_timer -= dt
            
            if self.combo_timer <= 0:
                # Combo perdido
                self.reset_combo()
    
    def reset_combo(self):
        """Reinicia el combo"""
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
        self.active_effects.clear()
    
    def get_score_multiplier(self):
        """Obtiene el multiplicador actual de puntuación"""
        return self.combo_multiplier
    
    def is_effect_active(self, effect):
        """Verifica si un efecto está activo"""
        return effect in self.active_effects


class WaveManager:
    """Gestor mejorado de oleadas con variedad"""
    
    def __init__(self):
        self.current_wave = 0
        self.wave_configs = []
        self.special_waves = {
            5: 'boss_wave',
            10: 'swarm_wave',
            15: 'elite_wave',
            20: 'survival_wave',
            25: 'mega_boss'
        }
        
    def get_wave_config(self, wave_number):
        """Genera configuración dinámica de oleada"""
        config = {
            'wave_number': wave_number,
            'enemy_count': self.calculate_enemy_count(wave_number),
            'enemy_types': self.get_enemy_distribution(wave_number),
            'spawn_delay': max(0.5, 3.0 - wave_number * 0.1),
            'modifiers': []
        }
        
        # Oleadas especiales
        if wave_number in self.special_waves:
            special_type = self.special_waves[wave_number]
            config = self.apply_special_wave(config, special_type)
        
        # Modificadores aleatorios cada 3 oleadas
        if wave_number % 3 == 0:
            config['modifiers'].extend(self.get_random_modifiers())
            
        return config
    
    def calculate_enemy_count(self, wave):
        """Calcula número de enemigos según la oleada"""
        base = 5
        growth = wave * 2
        
        # Límite para evitar spam excesivo
        return min(base + growth, 50)
    
    def get_enemy_distribution(self, wave):
        """Determina la distribución de tipos de enemigos"""
        distribution = []
        
        # Siempre hay soldados básicos
        distribution.append(('soldier', 0.4))
        
        # Añadir tipos según progresión
        if wave >= 2:
            distribution.append(('elite', 0.2))
        if wave >= 4:
            distribution.append(('kamikaze', 0.15))
        if wave >= 6:
            distribution.append(('sniper', 0.15))
        if wave >= 8:
            distribution.append(('officer', 0.1))
            
        # Normalizar probabilidades
        total = sum(prob for _, prob in distribution)
        distribution = [(enemy, prob/total) for enemy, prob in distribution]
        
        return distribution
    
    def apply_special_wave(self, config, special_type):
        """Aplica configuración especial a la oleada"""
        if special_type == 'boss_wave':
            config['enemy_count'] = 1
            config['enemy_types'] = [('boss', 1.0)]
            config['modifiers'].append('boss_fight')
            
        elif special_type == 'swarm_wave':
            config['enemy_count'] *= 2
            config['enemy_types'] = [('kamikaze', 0.8), ('soldier', 0.2)]
            config['spawn_delay'] = 0.2
            config['modifiers'].append('swarm')
            
        elif special_type == 'elite_wave':
            config['enemy_types'] = [('elite', 0.6), ('officer', 0.4)]
            config['modifiers'].append('elite_forces')
            
        elif special_type == 'survival_wave':
            config['enemy_count'] = 999  # Infinito
            config['modifiers'].append('survival_mode')
            config['time_limit'] = 60  # 60 segundos
            
        return config
    
    def get_random_modifiers(self):
        """Obtiene modificadores aleatorios para la oleada"""
        import random
        
        possible_modifiers = [
            'fast_enemies',      # Enemigos 50% más rápidos
            'tough_enemies',     # Enemigos con 50% más vida
            'fog_of_war',       # Visibilidad reducida
            'low_ammo',         # Munición limitada
            'regenerating',     # Enemigos se regeneran
            'explosive_death',  # Enemigos explotan al morir
            'darkness'          # Poca iluminación
        ]
        
        # 1-2 modificadores aleatorios
        num_modifiers = random.randint(1, 2)
        return random.sample(possible_modifiers, num_modifiers)