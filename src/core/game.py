"""
🎮 The main game logic module
"""

import logging
import random
import time
from datetime import datetime
from typing import List, Optional

from src.core.enums import SpinMode, Symbol
from src.core.reel import ReelSet
from src.models.spin_result import SpinResult
from src.ui.display import GameDisplay
from src.utils.config import (
    DEFAULT_BET,
    INITIAL_BALANCE,
    JACKPOT_INCREMENT,
    JACKPOT_SEED,
    MIN_BET,
    MAX_BET,
    PAYOUT_MULTIPLIERS,
)
from src.utils.sound import sound_manager

class StopSpinning(Exception):
    """Exception raised to stop the spinning animation"""
    pass

class SlotMachine:
    """
    🎰 The main slot machine game manager
    """
    
    def __init__(self, display: GameDisplay):
        """
        🎪 Sets up a new slot machine game
        
        Args:
            display: The game display manager
        """
        # Game state
        self.balance = INITIAL_BALANCE
        self.starting_balance = INITIAL_BALANCE
        self._bet = DEFAULT_BET
        self.jackpot = JACKPOT_SEED
        self.last_win = 0
        self.biggest_win = 0
        self.last_win_text = "No wins yet!"
        
        # Spin settings
        self.spin_mode = SpinMode.SINGLE
        self.auto_spinning = False
        self.spins_remaining = 0
        self.stop_requested = False
        
        # Game components
        self.reels = ReelSet()
        self.spin_history: List[SpinResult] = []
        self.session_start = datetime.now()
        
        # Display setup
        self.display = display
        
        logging.info("🎰 New slot machine initialized and ready for action!")
    
    def stop_auto_spin(self) -> None:
        """
        🛑 Stops auto-spinning mode
        """
        self.stop_requested = True
        self.auto_spinning = False
        self.spins_remaining = 0
        self.reels.stop_spin()
        logging.info("✋ Auto-spin stopped by player")
    
    def start_auto_spin(self) -> None:
        """
        🔄 Starts automatic spinning mode
        """
        # Don't start if already spinning
        if self.reels.spinning:
            return
            
        # If already auto-spinning, stop instead
        if self.auto_spinning:
            self.stop_auto_spin()
            return
        
        if self.balance < self._bet:
            logging.warning("❌ Not enough credits to spin!")
            return
            
        spins = {
            SpinMode.SINGLE: 1,
            SpinMode.FIVE: 5,
            SpinMode.TEN: 10,
            SpinMode.AUTO: 999999  # Basically infinite
        }
        
        self.stop_requested = False
        self.spins_remaining = spins[self.spin_mode]
        self.auto_spinning = True
        self._do_spin()
        logging.info(f"🔄 Starting auto-spin mode: {self.spin_mode.name}")
    
    def handle_auto_spin(self) -> None:
        """
        🎡 Processes one automatic spin
        """
        if not self.auto_spinning:
            return
            
        # If reels are spinning, just update them
        if self.reels.spinning:
            self.reels.update()
            return
            
        # If stop was requested, don't start another spin
        if self.stop_requested:
            logging.info("✋ Auto-spin complete")
            self.auto_spinning = False
            self.spins_remaining = 0
            return
            
        # If we can't afford another spin, stop
        if self.balance < self._bet:
            logging.info("❌ Auto-spin stopped: Insufficient funds")
            self.stop_auto_spin()
            return
            
        # If we just finished a spin, prepare for next one
        if self.spins_remaining > 0:
            self.spins_remaining -= 1
            if self.spins_remaining <= 0:
                logging.info("✋ Auto-spin complete")
                self.auto_spinning = False
            elif self.auto_spinning:  # Only start next spin if still auto-spinning
                time.sleep(0.2)  # Reduced delay between auto-spins
                self._do_spin()
    
    def _do_spin(self) -> None:
        """
        🎲 Performs a single spin of the slot machine
        """
        # Can't spin if we can't afford it!
        if self.balance < self._bet:
            logging.warning("❌ Insufficient funds for spin")
            self.stop_auto_spin()
            return
            
        # Place the bet
        old_balance = self.balance
        self.balance -= self._bet
        logging.debug(f"💰 Bet placed - Old balance: {old_balance}, Bet: {self._bet}, New balance: {self.balance}")
        
        # Start the reels spinning
        sound_manager.play("spin")
        self.reels.start_spin()
        
        try:
            # Spin each reel with increasing duration
            for reel_idx, reel in enumerate(self.reels.reels):
                # Initial fast spins
                spins = 20 + (reel_idx * 8)  # More spins for each subsequent reel
                
                # Fast spinning phase
                for _ in range(spins):
                    if not self.reels.spinning:
                        raise StopSpinning
                        
                    reel.rotate()
                    if random.random() < 0.3:  # 30% chance of double update
                        reel.rotate()
                        
                    # Update display after each rotation
                    self.display.draw_machine(
                        self.reels.get_visible_symbols(),
                        self.last_win,
                        self.jackpot,
                        self.balance,
                        self._bet,
                        self.spin_mode,
                        self.spins_remaining,
                        self.auto_spinning,
                        self.last_win_text
                    )
                    time.sleep(0.05)  # Fixed timing for smooth animation
                
                # Slowing down phase
                for i in range(5):
                    if not self.reels.spinning:
                        raise StopSpinning
                        
                    reel.rotate()
                    # Update display after each rotation
                    self.display.draw_machine(
                        self.reels.get_visible_symbols(),
                        self.last_win,
                        self.jackpot,
                        self.balance,
                        self._bet,
                        self.spin_mode,
                        self.spins_remaining,
                        self.auto_spinning,
                        self.last_win_text
                    )
                    time.sleep(0.1 + (i * 0.05))
            
            # Stop spinning
            self.reels.stop_spin()
            
            # Check what we won
            win_amount, is_jackpot = self.reels.check_win(self._bet)
            
            # Handle jackpot wins
            if is_jackpot:
                old_win = win_amount
                win_amount += self.jackpot
                sound_manager.play("jackpot")
                self.jackpot = JACKPOT_SEED  # Reset jackpot
                winning_symbols = " ".join(str(s.value) for s in self.reels.get_visible_symbols()[1])  # Middle row
                self.last_win_text = f"★ JACKPOT {win_amount:,} | {winning_symbols} ★"
                logging.info(f"🎊 JACKPOT WIN! Base: {old_win}, Jackpot: {self.jackpot}, Total: {win_amount}")
            else:
                self.jackpot += JACKPOT_INCREMENT  # Increase jackpot
                if win_amount > 0:
                    sound_manager.play("win")
                    winning_symbols = " ".join(str(s.value) for s in self.reels.get_visible_symbols()[1])  # Middle row
                    self.last_win_text = f"▶ Win {win_amount:,} | {winning_symbols} ◀"
                    logging.info(f"🌟 Win! Amount: {win_amount}")
                else:
                    self.last_win_text = "No wins yet!"
            
            # Update game state
            old_balance = self.balance
            self.balance += win_amount
            self.last_win = win_amount
            self.biggest_win = max(self.biggest_win, win_amount)
            
            logging.debug(f"💰 Balance update - Old: {old_balance}, Win: {win_amount}, New: {self.balance}")
            
            # Record this spin
            self.spin_history.append(SpinResult(
                symbols=self.reels.get_visible_symbols()[1],  # Middle row only
                bet_amount=self._bet,
                win_amount=win_amount,
                timestamp=datetime.now(),
                is_jackpot=is_jackpot,
                jackpot_amount=self.jackpot if is_jackpot else None
            ))
            
        except StopSpinning:
            logging.info("Spin interrupted by player")
            self.reels.stop_spin()
            self.auto_spinning = False  # Make sure auto-spinning stops too
            self.spins_remaining = 0
    
    def get_visible_symbols(self) -> List[List[Symbol]]:
        """
        👀 Gets the symbols currently showing on all reels
        
        Returns:
            List[List[Symbol]]: All visible symbols (3 rows, 3 columns)
        """
        return self.reels.get_visible_symbols()
    
    @property
    def balance(self) -> int:
        """
        💰 The current balance
        """
        return self._balance

    @balance.setter
    def balance(self, value: int) -> None:
        """
        💰 Sets a new balance amount
        """
        old_balance = getattr(self, '_balance', None)
        self._balance = int(value)  # Ensure integer
        if old_balance is not None:  # Skip logging initial balance set
            logging.debug(f"💰 Game balance changed: {old_balance} -> {self._balance} (Δ{self._balance - old_balance})")

    @property
    def bet(self) -> int:
        """
        💰 The current bet amount
        """
        return self._bet
    
    @bet.setter
    def bet(self, value: int) -> None:
        """
        💰 Sets a new bet amount
        """
        # Keep bet within allowed range
        self._bet = max(MIN_BET, min(value, MAX_BET))
        # Can't bet more than we have!
        self._bet = min(self._bet, self.balance)
        logging.debug(f"💰 Bet amount changed to: {self._bet}")