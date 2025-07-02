import pygame
import os
import random

class AudioManager:
    """Gestor centralizado de audio para el juego"""
    
    def __init__(self):
        # Inicializar mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Volúmenes
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        # Diccionarios para almacenar sonidos
        self.sounds = {}
        self.music_tracks = {}
        
        # Estado de la música
        self.current_music = None
        self.music_paused = False
        
        # Cargar sonidos
        self.load_sounds()
        
    def load_sounds(self):
        """Carga todos los sonidos del juego"""
        # Rutas base
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sounds_path = os.path.join(base_path, "assets", "sounds")
        music_path = os.path.join(base_path, "assets", "music")
        
        # Crear directorios si no existen
        os.makedirs(sounds_path, exist_ok=True)
        os.makedirs(music_path, exist_ok=True)
        
        # Diccionario de sonidos a cargar
        sound_files = {
            # Disparos
            "player_shoot": "player_shoot.wav",
            "enemy_shoot": "enemy_shoot.wav",
            "shotgun": "shotgun.wav",
            
            # Explosiones
            "explosion_small": "explosion_small.wav",
            "explosion_big": "explosion_big.wav",
            "grenade": "grenade.wav",
            
            # Impactos
            "bullet_hit": "bullet_hit.wav",
            "player_hurt": "player_hurt.wav",
            "enemy_hurt": "enemy_hurt.wav",
            "metal_hit": "metal_hit.wav",
            
            # Power-ups
            "powerup_health": "powerup_health.wav",
            "powerup_ammo": "powerup_ammo.wav",
            "powerup_speed": "powerup_speed.wav",
            
            # UI
            "menu_select": "menu_select.wav",
            "menu_confirm": "menu_confirm.wav",
            "menu_back": "menu_back.wav",
            "game_over": "game_over.wav",
            "victory": "victory.wav",
            
            # Enemigos
            "enemy_alert": "enemy_alert.wav",
            "kamikaze_scream": "kamikaze_scream.wav",
            "officer_command": "officer_command.wav",
            
            # Ambiente
            "footsteps": "footsteps.wav",
            "reload": "reload.wav",
            "empty_gun": "empty_gun.wav",
        }
        
        # Cargar cada sonido
        for name, filename in sound_files.items():
            filepath = os.path.join(sounds_path, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    print(f"✓ Sonido cargado: {name}")
                except:
                    print(f"✗ Error cargando sonido: {name}")
                    # Crear sonido vacío como placeholder
                    self.sounds[name] = self.create_placeholder_sound()
            else:
                # Crear sonido placeholder si no existe el archivo
                self.sounds[name] = self.create_placeholder_sound()
                print(f"⚠ Sonido no encontrado: {name} - usando placeholder")
        
        # Música
        music_files = {
            "menu_theme": "menu_theme.ogg",
            "battle_theme": "battle_theme.ogg",
            "boss_theme": "boss_theme.ogg",
            "victory_theme": "victory_theme.ogg",
            "game_over_theme": "game_over_theme.ogg",
        }
        
        for name, filename in music_files.items():
            filepath = os.path.join(music_path, filename)
            if os.path.exists(filepath):
                self.music_tracks[name] = filepath
                print(f"✓ Música cargada: {name}")
            else:
                print(f"⚠ Música no encontrada: {name}")
    
    def create_placeholder_sound(self):
        """Crea un sonido silencioso como placeholder"""
        # Crear un sonido muy corto y silencioso
        placeholder = pygame.mixer.Sound(buffer=bytes([128] * 100))
        placeholder.set_volume(0)
        return placeholder
    
    def play_sound(self, sound_name, volume=1.0, loops=0):
        """Reproduce un efecto de sonido"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.sfx_volume * volume * self.master_volume)
            channel = sound.play(loops)
            return channel
        else:
            print(f"Sonido no encontrado: {sound_name}")
            return None
    
    def play_random_sound(self, sound_names, volume=1.0):
        """Reproduce un sonido aleatorio de una lista"""
        if sound_names:
            sound_name = random.choice(sound_names)
            return self.play_sound(sound_name, volume)
        return None
    
    def play_music(self, music_name, loops=-1, fade_ms=1000):
        """Reproduce música de fondo"""
        if music_name in self.music_tracks:
            if self.current_music != music_name:
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(self.music_tracks[music_name])
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self.current_music = music_name
                self.music_paused = False
        else:
            print(f"Música no encontrada: {music_name}")
    
    def stop_music(self, fade_ms=1000):
        """Detiene la música"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
        self.music_paused = False
    
    def pause_music(self):
        """Pausa la música"""
        if self.current_music and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True
    
    def unpause_music(self):
        """Reanuda la música"""
        if self.current_music and self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
    
    def set_master_volume(self, volume):
        """Establece el volumen maestro (0.0 a 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        self.update_volumes()
    
    def set_sfx_volume(self, volume):
        """Establece el volumen de efectos (0.0 a 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Establece el volumen de música (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def update_volumes(self):
        """Actualiza todos los volúmenes"""
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        # Los sonidos se actualizan cuando se reproducen
    
    def play_footstep(self):
        """Reproduce sonido de pasos"""
        # Variar el pitch para hacer más realista
        sound = self.sounds.get("footsteps")
        if sound:
            # Clonar el sonido para no afectar el original
            temp_sound = sound
            temp_sound.set_volume(self.sfx_volume * 0.3 * self.master_volume)
            temp_sound.play()
    
    def play_explosion(self, size="small"):
        """Reproduce sonido de explosión según tamaño"""
        if size == "big":
            self.play_sound("explosion_big", 0.8)
        else:
            self.play_sound("explosion_small", 0.6)
    
    def play_impact(self, material="flesh"):
        """Reproduce sonido de impacto según material"""
        if material == "metal":
            self.play_sound("metal_hit", 0.7)
        elif material == "flesh":
            self.play_random_sound(["enemy_hurt", "bullet_hit"], 0.6)
        else:
            self.play_sound("bullet_hit", 0.5)
    
    def create_sound_variations(self, base_sound, num_variations=3):
        """Crea variaciones de un sonido cambiando el pitch"""
        # TODO: Implementar variaciones de sonido para más realismo
        pass

# Instancia global del gestor de audio
audio_manager = None

def get_audio_manager():
    """Obtiene la instancia global del gestor de audio"""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager