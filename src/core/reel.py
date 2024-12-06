"""
🎰 Slot Machine Reels - Where the magic happens!
"""

import random
import time
from typing import List, Optional, Tuple
import logging

from src.core.enums import Symbol
from src.utils.config import PAYOUT_MULTIPLIERS

class Reel:
    """
    🎡 A single spinning reel of our slot machine
    """
    
    def __init__(self):
        """
        🎰 Creates a new slot machine reel
        """
        self.symbols = [
            Symbol.CHERRY,
            Symbol.LEMON,
            Symbol.ORANGE,
            Symbol.GRAPE,
            Symbol.DIAMOND,
            Symbol.MONEY,
            Symbol.DICE,
            Symbol.STAR
        ] * 3  # Triplicate for more combinations
        
        random.shuffle(self.symbols)
        self.position = 0
        self.length = len(self.symbols)
        
    def rotate(self) -> None:
        """
        Rotate the reel by one position
        """
        self.position = (self.position + 1) % self.length

    def get_visible_symbols(self) -> List[Symbol]:
        """
        Get the three visible symbols (above, current, below)
        """
        symbols = []
        for offset in range(-1, 2):
            idx = (self.position + offset) % self.length
            symbols.append(self.symbols[idx])
        return symbols

class ReelSet:
    """
    🎰 The complete set of reels in our slot machine
    """
    
    def __init__(self, num_reels: int = 3):
        """
        🎪 Creates the complete set of reels
        
        Args:
            num_reels: How many reels to create (usually 3)
        """
        self.reels = [Reel() for _ in range(num_reels)]
        self.spinning = False
    
    def start_spin(self) -> None:
        """
        🌪️ Start spinning all reels
        """
        self.spinning = True
    
    def stop_spin(self) -> None:
        """
        ✋ Stop all reels immediately
        """
        self.spinning = False
    
    def update(self) -> None:
        """
        🔄 Updates all spinning reels
        """
        if not self.spinning:
            return
            
        # Update each reel
        for reel in self.reels:
            reel.rotate()
    
    def get_visible_symbols(self) -> List[List[Symbol]]:
        """
        👀 Gets all visible symbols from all reels
        
        Returns:
            List[List[Symbol]]: Visible symbols for each reel
        """
        return [reel.get_visible_symbols() for reel in self.reels]
    
    def check_win(self, bet_amount: int) -> Tuple[int, bool]:
        """
        🎯 Checks if the current symbols make a winning combination
        
        Args:
            bet_amount: How much was bet on this spin
        
        Returns:
            Tuple[int, bool]: (Amount won, Whether it's a jackpot)
        """
        # Get middle row symbols (the payline)
        symbols = [reel.get_visible_symbols()[1] for reel in self.reels]
        logging.debug(f"🎯 Checking win - Symbols: {[s.name for s in symbols]}, Bet: {bet_amount}")
        
        # Check for jackpot (all stars)
        if all(s == Symbol.STAR for s in symbols):
            win_amount = bet_amount * PAYOUT_MULTIPLIERS[Symbol.STAR.name]
            logging.debug(f"🌟 JACKPOT WIN! Amount: {win_amount}")
            return win_amount, True
        
        # First, find the non-wild symbols in the middle row
        non_wild_symbols = [s for s in symbols if s != Symbol.STAR]
        logging.debug(f"🎲 Non-wild symbols: {[s.name for s in non_wild_symbols]}")
        
        if not non_wild_symbols:
            # All symbols are Wilds; use highest payout
            actual_symbol = Symbol.MONEY  # Highest paying regular symbol
            logging.debug("💫 All wilds! Using MONEY symbol for highest payout")
        else:
            # Use the most common non-wild symbol
            actual_symbol = max(set(non_wild_symbols), key=non_wild_symbols.count)
            logging.debug(f"🎯 Most common symbol: {actual_symbol.name}")
            
        # Check if all symbols are the same when considering Wilds
        is_win = all(s == actual_symbol or s == Symbol.STAR for s in symbols)
        if is_win:
            win_amount = bet_amount * PAYOUT_MULTIPLIERS[actual_symbol.name]
            logging.debug(f"💰 Regular win! Symbol: {actual_symbol.name}, Multiplier: {PAYOUT_MULTIPLIERS[actual_symbol.name]}x, Amount: {win_amount}")
            return win_amount, False
            
        logging.debug("❌ No win")
        return 0, False  # No win