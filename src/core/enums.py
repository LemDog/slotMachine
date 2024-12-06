"""
🎲 Game Enumerations - The building blocks of our slot machine!

This module contains all the important enums (special constants) that make our game tick.
Think of these as the "settings" that control how different parts of the game behave.
"""

from enum import Enum, auto

class SpinMode(Enum):
    """
    🎰 Different ways to spin the slots!
    
    Available modes:
    - SINGLE: One spin at a time (for the careful player)
    - FIVE: 5 automatic spins (for the casual player)
    - TEN: 10 automatic spins (for the enthusiast)
    - AUTO: Continuous spins until stopped (for the brave!)
    """
    SINGLE = auto()  # Just one spin - perfect for beginners!
    FIVE = auto()    # 5 spins - a nice short session
    TEN = auto()     # 10 spins - getting serious!
    AUTO = auto()    # Non-stop action until you say when!

class Symbol(Enum):
    """
    ✨ All the shiny symbols that can appear on the reels!
    
    Each symbol has a different payout value:
    🍒 CHERRY  - The classic (2x)
    🍋 LEMON   - A zesty win (3x)
    🍊 ORANGE  - Sweet returns (4x)
    🍇 GRAPE   - Juicy rewards (5x)
    💎 DIAMOND - Luxurious wins (10x)
    💰 MONEY   - Big money time! (15x)
    🎲 DICE    - Take a chance (20x)
    🌟 STAR    - The golden prize! (50x)
    """
    CHERRY = "🍒"   # A fruity favorite!
    LEMON = "🍋"    # When life gives you lemons...
    ORANGE = "🍊"   # Not just for breakfast
    GRAPE = "🍇"    # A bunch of wins
    DIAMOND = "💎"  # A player's best friend
    MONEY = "💰"    # Cha-ching!
    DICE = "🎲"     # Roll the dice
    STAR = "🌟"     # Reach for the stars!
 