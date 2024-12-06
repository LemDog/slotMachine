"""
⚙️ Game configuration constants
"""

# Game settings
INITIAL_BALANCE = 1000
DEFAULT_BET = 10
MIN_BET = 1
MAX_BET = 100
JACKPOT_SEED = 1000
JACKPOT_INCREMENT = 10

# Display settings
FRAME_WIDTH = 60
FRAME_HEIGHT = 25
SECTION_TITLE_WIDTH = 20
SYMBOL_SPACING = " "
LEFT_MARGIN = 8

# Animation settings
SCREEN_REFRESH_RATE = 50  # Milliseconds (20 FPS)

# Sound settings
ENABLE_SOUND = True
SOUND_VOLUME = 0.5

# Statistics settings
MAX_HISTORY_SIZE = 1000  # How many spins to remember
CHART_UPDATE_RATE = 5    # Update charts every X spins

# Payout settings
PAYOUT_MULTIPLIERS = {
    "CHERRY": 2,    # 🍒
    "LEMON": 3,     # 🍋
    "ORANGE": 4,    # 🍊
    "GRAPE": 5,     # 🍇
    "DIAMOND": 10,  # 💎
    "MONEY": 15,    # 💰
    "DICE": 20,     # 🎲
    "STAR": 50      # 🌟
}