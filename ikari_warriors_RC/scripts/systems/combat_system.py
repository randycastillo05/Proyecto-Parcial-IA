import pygame
import math
import random
import colorsys
from scripts.utils.constants import *
from scripts.utils.enhanced_visual import VisualEffects
from scripts.utils.game_feel import CombatEffects

class CombatSystem:
    """Sistema de combate mejorado con combos y efectos especiales"""
    
    def __init__(self, game):
        self.game = game
        
        # Sistema de combo
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 2.0
        self.combo_multiplier = 1.0
        self.max_combo = 0
        
        # Hitos de combo con recompensas
        self.combo_milestones = {
            5: {
                'multiplier': 1.5, 
                'effect': 'speed_boost',
                'message': '¡COMBO x5! Velocidad aumentada'
            },
            10: {
                'multiplier': 2.0, 
                'effect': 'damage_boost',
                'message': '¡COMBO x10! Daño aumentado'
            },
            15: {
                'multiplier': 2.5, 
                'effect': 'fire_rate_boost',
                'message': '¡COMBO x15! Cadencia mejorada'
            },
            25: {
                'multiplier': 3.0, 
                'effect': 'explosive_rounds',
                'message': '¡COMBO x25! Balas explosivas'
            },
            50: {
                'multiplier': 5.0, 
                'effect': 'god_mode',
                'message': '¡COMBO x50! MODO DIOS'
            }
        }
        
        # Efectos activos
        self.active_effects = set()
        self.effect_timers = {}
        
        # Estadísticas de combate
        self.kills_this_wave = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        
        # Efectos visuales de combate
        self.damage_numbers = []
        self.combo_announcements = []
        self.kill_streak_timer = 0
        self.multi_kill_count = 0
        
    def add_kill(self, enemy_type, position):
        """Registra una eliminación y actualiza combos"""
        self.kills_this_wave += 1
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        
        # Actualizar racha de multi-kills
        if self.kill_streak_timer > 0:
            self.multi_kill_count += 1
        else:
            self.multi_kill_count = 1
        self.kill_streak_timer = 0.5  # Ventana para multi-kills
        
        # Calcular puntos con multiplicador
        base_score = {
            EnemyType.SOLDIER: 100,
            EnemyType.ELITE: 200,
            EnemyType.SNIPER: 300,
            EnemyType.KAMIKAZE: 150,
            EnemyType.OFFICER: 500
        }.get(enemy_type, 100)
        
        final_score = int(base_score * self.combo_multiplier)
        self.game.score += final_score
        
        # Añadir número de daño flotante
        self.add_damage_number(position, final_score, is_score=True)
        
        # Verificar hitos de combo
        for milestone, rewards in self.combo_milestones.items():
            if self.combo_count == milestone:
                self.combo_multiplier = rewards['multiplier']
                self.activate_combo_effect(rewards['effect'])
                self.add_combo_announcement(rewards['message'], milestone)
                
                # Efectos especiales para hitos grandes
                if milestone >= 25:
                    self.game.add_screen_shake(10, 0.3)
                    self.game.screen_flash = True
                
        # Actualizar combo máximo
        self.max_combo = max(self.max_combo, self.combo_count)
        
        # Verificar multi-kills
        self.check_multi_kill()
        
        # Efectos de audio
        if self.game.audio_manager:
            if self.combo_count > 10:
                self.game.audio_manager.play_sound("combo_high", 0.7)
            elif self.combo_count > 5:
                self.game.audio_manager.play_sound("combo_medium", 0.6)
            else:
                self.game.audio_manager.play_sound("enemy_death", 0.5)
    
    def check_multi_kill(self):
        """Verifica y recompensa multi-kills"""
        multi_kill_names = {
            2: ("Double Kill!", 200),
            3: ("Triple Kill!", 500),
            4: ("Quad Kill!", 1000),
            5: ("Penta Kill!", 2000),
            6: ("MONSTER KILL!", 5000)
        }
        
        if self.multi_kill_count in multi_kill_names:
            name, bonus = multi_kill_names[self.multi_kill_count]
            self.game.score += bonus
            self.add_combo_announcement(name, self.multi_kill_count, special=True)
            
            # Efectos especiales
            self.game.add_screen_shake(self.multi_kill_count * 2, 0.2)
    
    def activate_combo_effect(self, effect):
        """Activa un efecto de combo"""
        self.active_effects.add(effect)
        
        if effect == 'speed_boost':
            self.game.player.apply_speed_boost(1.5, 10.0)
            self.effect_timers[effect] = 10.0
            
        elif effect == 'damage_boost':
            self.game.player.apply_damage_boost(2.0, 10.0)
            self.effect_timers[effect] = 10.0
            
        elif effect == 'fire_rate_boost':
            self.game.player.apply_fire_rate_boost(2.0, 10.0)
            self.effect_timers[effect] = 10.0
            
        elif effect == 'explosive_rounds':
            # Las balas causan explosiones pequeñas
            self.effect_timers[effect] = 15.0
            
        elif effect == 'god_mode':
            # Invencibilidad temporal
            self.game.player.invulnerable = True
            self.game.player.invulnerable_timer = 5.0
            self.effect_timers[effect] = 5.0
    
    def update(self, dt):
        """Actualiza el sistema de combate"""
        # Actualizar combo
        if self.combo_timer > 0:
            self.combo_timer -= dt
            
            if self.combo_timer <= 0:
                self.reset_combo()
        
        # Actualizar timers de efectos
        effects_to_remove = []
        for effect, timer in self.effect_timers.items():
            self.effect_timers[effect] -= dt
            if self.effect_timers[effect] <= 0:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            self.active_effects.remove(effect)
            del self.effect_timers[effect]
        
        # Actualizar kill streak timer
        if self.kill_streak_timer > 0:
            self.kill_streak_timer -= dt
        
        # Actualizar números de daño
        for damage_num in self.damage_numbers[:]:
            damage_num['timer'] -= dt
            damage_num['y'] -= damage_num['vy'] * dt
            damage_num['vy'] -= 100 * dt  # Gravedad
            
            if damage_num['timer'] <= 0:
                self.damage_numbers.remove(damage_num)
        
        # Actualizar anuncios de combo
        for announcement in self.combo_announcements[:]:
            announcement['timer'] -= dt
            if announcement['timer'] <= 0:
                self.combo_announcements.remove(announcement)
    
    def reset_combo(self):
        """Reinicia el combo"""
        if self.combo_count > 0:
            # Guardar estadísticas
            if self.combo_count > 10:
                print(f"Combo perdido: x{self.combo_count}")
            
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
        self.active_effects.clear()
        self.effect_timers.clear()
    
    def add_damage_number(self, position, damage, critical=False, is_score=False):
        """Añade un número de daño flotante"""
        color = (255, 255, 0) if is_score else (255, 255, 255)
        if critical:
            color = (255, 100, 0)
            damage = f"{damage}!"
        
        self.damage_numbers.append({
            'x': position[0] + random.randint(-10, 10),
            'y': position[1],
            'vy': -150,
            'text': str(damage),
            'color': color,
            'size': 32 if critical else 24,
            'timer': 1.0,
            'is_score': is_score
        })
    
    def add_combo_announcement(self, text, combo_level, special=False):
        """Añade un anuncio de combo"""
        self.combo_announcements.append({
            'text': text,
            'timer': 2.0,
            'combo_level': combo_level,
            'special': special
        })
    
    def process_hit(self, bullet, target):
        """Procesa un impacto de bala"""
        self.shots_hit += 1
        
        # Calcular daño
        damage = bullet.damage
        
        # Verificar crítico
        critical_chance = 0.05  # 5% base
        if hasattr(self.game.player, 'critical_chance'):
            critical_chance = self.game.player.critical_chance
        
        is_critical = random.random() < critical_chance
        if is_critical:
            damage *= 2
        
        # Aplicar daño
        target.take_damage(damage)
        self.damage_dealt += damage
        
        # Efectos visuales
        self.add_damage_number(target.pos, damage, is_critical)
        
        # Efectos especiales según combo
        if 'explosive_rounds' in self.active_effects:
            # Las balas explotan
            self.game.create_explosion(
                bullet.pos.x, bullet.pos.y, 
                radius=30, damage=damage // 2
            )
        
        # Partículas de impacto
        self.game.particle_system.create_blood_splatter(
            target.pos.x, target.pos.y, bullet.angle
        )
        
        # Hit stop para game feel
        self.game.game_feedback.add_hit_stop(0.02)
        
        # Si el objetivo muere
        if target.health <= 0:
            self.add_kill(target.enemy_type, (target.pos.x, target.pos.y))
    
    def draw_ui(self, screen):
        """Dibuja la UI del sistema de combate"""
        # Dibujar combo actual
        if self.combo_count > 1:
            self.draw_combo_meter(screen)
        
        # Dibujar números de daño
        font = pygame.font.Font(None, 24)
        for damage_num in self.damage_numbers:
            # Efecto de escala
            scale = 1.0 + (1.0 - damage_num['timer']) * 0.5
            scaled_size = int(damage_num['size'] * scale)
            damage_font = pygame.font.Font(None, scaled_size)
            
            # Renderizar con sombra
            shadow_surf = damage_font.render(damage_num['text'], True, (0, 0, 0))
            text_surf = damage_font.render(damage_num['text'], True, damage_num['color'])
            
            # Posición con efecto de flotación
            x = int(damage_num['x'])
            y = int(damage_num['y'])
            
            screen.blit(shadow_surf, (x + 2, y + 2))
            screen.blit(text_surf, (x, y))
        
        # Dibujar anuncios de combo
        self.draw_combo_announcements(screen)
        
        # Dibujar efectos activos
        self.draw_active_effects(screen)
    
    def draw_combo_meter(self, screen):
        """Dibuja el medidor de combo"""
        # Posición y tamaño
        meter_x = SCREEN_WIDTH // 2 - 100
        meter_y = 100
        meter_width = 200
        meter_height = 20
        
        # Calcular progreso del timer
        timer_progress = self.combo_timer / self.combo_timeout
        
        # Color según nivel de combo
        if self.combo_count >= 25:
            color = (255, 0, 255)  # Magenta
        elif self.combo_count >= 15:
            color = (255, 0, 0)    # Rojo
        elif self.combo_count >= 10:
            color = (255, 165, 0)  # Naranja
        elif self.combo_count >= 5:
            color = (255, 255, 0)  # Amarillo
        else:
            color = (0, 255, 0)    # Verde
        
        # Dibujar barra de fondo
        pygame.draw.rect(screen, (50, 50, 50), 
                        (meter_x, meter_y, meter_width, meter_height))
        
        # Dibujar barra de progreso
        progress_width = int(meter_width * timer_progress)
        if progress_width > 0:
            pygame.draw.rect(screen, color,
                           (meter_x, meter_y, progress_width, meter_height))
        
        # Borde
        pygame.draw.rect(screen, WHITE,
                        (meter_x, meter_y, meter_width, meter_height), 2)
        
        # Texto del combo
        font = pygame.font.Font(None, 48)
        combo_text = f"COMBO x{self.combo_count}"
        
        # Efecto de pulso
        pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1
        scaled_font = pygame.font.Font(None, int(48 * pulse))
        
        text_surf = scaled_font.render(combo_text, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, meter_y - 30))
        screen.blit(text_surf, text_rect)
        
        # Multiplicador
        mult_font = pygame.font.Font(None, 24)
        mult_text = f"Score x{self.combo_multiplier:.1f}"
        mult_surf = mult_font.render(mult_text, True, WHITE)
        mult_rect = mult_surf.get_rect(center=(SCREEN_WIDTH // 2, meter_y + meter_height + 10))
        screen.blit(mult_surf, mult_rect)
    
    def draw_combo_announcements(self, screen):
        """Dibuja los anuncios de combo"""
        y_offset = 200
        
        for announcement in self.combo_announcements:
            # Calcular alpha
            alpha = min(255, int(announcement['timer'] * 255))
            
            # Tamaño y efecto según tipo
            if announcement['special']:
                size = 64
                # Efecto arcoíris para multi-kills
                hue = int((pygame.time.get_ticks() / 10) % 360)
                # Crear color RGB desde HSL manualmente para evitar problemas
                import colorsys
                rgb = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
                color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            else:
                size = 48
                color = (255, 255, 0)
            
            # Efecto de escala
            scale = 1.0 + (2.0 - announcement['timer']) * 0.5
            scaled_size = int(size * scale)
            
            font = pygame.font.Font(None, scaled_size)
            
            # Crear superficie con alpha
            text_surf = font.render(announcement['text'], True, color)
            text_surf.set_alpha(alpha)
            
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            
            y_offset += scaled_size + 10
    
    def draw_active_effects(self, screen):
        """Dibuja los efectos activos"""
        x = 10
        y = 200
        
        font = pygame.font.Font(None, 24)
        
        effect_names = {
            'speed_boost': ('⚡ Velocidad', (0, 255, 255)),
            'damage_boost': ('💪 Daño x2', (255, 100, 0)),
            'fire_rate_boost': ('🔥 Cadencia', (255, 255, 0)),
            'explosive_rounds': ('💥 Explosivas', (255, 0, 0)),
            'god_mode': ('⭐ INVENCIBLE', (255, 0, 255))
        }
        
        for effect in self.active_effects:
            if effect in effect_names and effect in self.effect_timers:
                name, color = effect_names[effect]
                timer = self.effect_timers[effect]
                
                # Fondo
                bg_rect = pygame.Rect(x - 5, y - 2, 150, 24)
                bg_surface = pygame.Surface((150, 24), pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))
                screen.blit(bg_surface, (x - 5, y - 2))
                pygame.draw.rect(screen, color, bg_rect, 2)
                
                # Texto
                text = f"{name}: {timer:.1f}s"
                text_surf = font.render(text, True, color)
                screen.blit(text_surf, (x, y))
                
                y += 30
    
    def get_accuracy(self):
        """Calcula la precisión actual"""
        if self.shots_fired == 0:
            return 1.0
        return self.shots_hit / self.shots_fired
    
    def reset_wave_stats(self):
        """Reinicia las estadísticas de la oleada"""
        self.kills_this_wave = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.reset_combo()