"""
🎵 Sound Effects Manager - Adding some musical flair to your wins!

This module handles all the fun sound effects that make the game more exciting.
From the satisfying click of the spin button to the triumphant fanfare of a
big win, these sounds make every spin more thrilling! 🎶
"""

import logging
from pathlib import Path
from typing import Dict, Optional

try:
    import simpleaudio as sa
    SOUND_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SOUND_AVAILABLE = False
    logging.warning("🔇 Sound support not available - game will run in silent mode")

from src.utils.config import ENABLE_SOUND, SOUND_VOLUME

class SoundManager:
    """
    🔊 The maestro of our slot machine's symphony!
    
    This class loads and plays all our wonderful sound effects. It's like
    a tiny DJ for the slot machine! 
    
    Features:
    - 🎵 Manages all game sound effects
    - 🔇 Respects the sound enable/disable setting
    - 🎚️ Controls volume levels
    - 💾 Efficient sound loading and caching
    """
    
    def __init__(self):
        """
        🎼 Sets up our sound system and loads all the effects
        """
        self.sounds: Dict[str, Optional[sa.WaveObject]] = {}
        self.current_play: Optional[sa.PlayObject] = None
        self.sound_enabled = ENABLE_SOUND and SOUND_AVAILABLE
        
        if self.sound_enabled:
            self._load_sound_effects()
        else:
            logging.info("🔇 Sound system initialized in silent mode")
    
    def _load_sound_effects(self) -> None:
        """
        📂 Loads all our awesome sound effects from files
        
        Sound effects included:
        - 🎲 spin.wav: The satisfying click when you spin
        - 💰 win.wav: Cha-ching! You won something!
        - 🌟 bigwin.wav: For those extra special wins
        - 🎊 jackpot.wav: The grand celebration sound!
        """
        sound_dir = Path("assets/sounds")
        if not sound_dir.exists():
            logging.warning(f"🔇 Sound directory not found: {sound_dir}")
            self.sound_enabled = False
            return
            
        sound_files = {
            "spin": "spin.wav",
            "win": "win.wav",
            "bigwin": "bigwin.wav",
            "jackpot": "jackpot.wav"
        }
        
        for name, filename in sound_files.items():
            try:
                path = sound_dir / filename
                if path.exists():
                    self.sounds[name] = sa.WaveObject.from_wave_file(str(path))
                    logging.debug(f"🎵 Loaded sound effect: {name}")
                else:
                    logging.warning(f"🔇 Sound file not found: {filename}")
                    self.sounds[name] = None
            except Exception as e:
                logging.warning(f"🔇 Couldn't load sound '{name}': {e}")
                self.sounds[name] = None
    
    def play(self, sound_name: str) -> None:
        """
        🎵 Plays a specific sound effect
        
        Args:
            sound_name (str): Which sound to play ('spin', 'win', 'bigwin', 'jackpot')
        """
        if not self.sound_enabled:
            return
            
        if sound := self.sounds.get(sound_name):
            try:
                # Stop any currently playing sound
                if self.current_play and self.current_play.is_playing():
                    self.current_play.stop()
                
                # Play the new sound
                self.current_play = sound.play()
                # Adjust volume (if supported by platform)
                try:
                    self.current_play.set_volume(SOUND_VOLUME)
                except AttributeError:
                    pass  # Volume control not supported on this platform
            except Exception as e:
                logging.warning(f"🔇 Error playing sound '{sound_name}': {e}")
    
    def stop_all(self) -> None:
        """
        🔇 Stops any currently playing sound effects
        """
        if self.sound_enabled and self.current_play and self.current_play.is_playing():
            try:
                self.current_play.stop()
            except Exception as e:
                logging.warning(f"🔇 Error stopping sounds: {e}")

# Global sound manager instance
sound_manager = SoundManager() 