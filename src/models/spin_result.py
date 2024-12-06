"""
🎯 Spin Result - Tracking what happens when those reels stop spinning!

This module defines the SpinResult class that captures all the exciting details
of what happens after each spin. It's like a snapshot of your moment of glory
(or just another spin - they can't all be winners! 😉)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src.core.enums import Symbol

@dataclass
class SpinResult:
    """
    📝 A detailed record of a single spin result
    
    This class is like a receipt for your spin - it keeps track of:
    - What symbols you landed on
    - How much you bet
    - How much you won (if anything!)
    - When it happened
    - Whether you hit the jackpot 🎉
    
    Attributes:
        symbols (List[Symbol]): The symbols that landed on the payline
        bet_amount (int): How many credits you wagered
        win_amount (int): How many credits you won (0 if no win)
        timestamp (datetime): When this spin happened
        is_jackpot (bool): Did you hit the big one? 🎊
        jackpot_amount (Optional[int]): How much the jackpot paid (if you won it)
    """
    
    symbols: List[Symbol]         # The winning (or losing) combination
    bet_amount: int              # Your brave wager
    win_amount: int              # Your glorious winnings
    timestamp: datetime          # The moment of truth
    is_jackpot: bool = False     # Did you strike gold?
    jackpot_amount: Optional[int] = None  # The jackpot bounty
    
    def __str__(self) -> str:
        """
        ✨ Creates a pretty string representation of the spin result
        
        Returns:
            str: A nice summary of what happened in this spin
        """
        symbols_str = " ".join(symbol.value for symbol in self.symbols)
        result = f"Spin Result: {symbols_str}\n"
        result += f"Bet: {self.bet_amount} 💰 | "
        result += f"Win: {self.win_amount} 💰\n"
        
        if self.is_jackpot:
            result += f"🎊 JACKPOT WIN! {self.jackpot_amount} 💰 🎊\n"
            
        return result 