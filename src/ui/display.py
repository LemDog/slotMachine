"""
🎨 Game Display - Making our slot machine look beautiful!

This module handles all the visual aspects of our game, from drawing the slot
machine frame to showing animations. It's like the artist of our game, making
everything look pretty and engaging! 🖼️
"""

import curses
import logging
from typing import List, Optional, Tuple

from src.core.enums import SpinMode, Symbol
from src.utils.config import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    SECTION_TITLE_WIDTH,
    SYMBOL_SPACING,
    LEFT_MARGIN,
    PAYOUT_MULTIPLIERS,
)

class GameDisplay:
    """
    🖼️ The artist behind our beautiful slot machine display!
    """    
    def __init__(self, stdscr: 'curses.window'):
        """
        🎨 Initializes the game display
        
        Args:
            stdscr: The main curses window
        """
        self.screen = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Check if terminal is big enough
        min_height = 25  # Increased height for better spacing
        min_width = FRAME_WIDTH + 4
        
        if self.height < min_height or self.width < min_width:
            raise ValueError(
                f"Terminal too small! Need at least {min_width}x{min_height}, "
                f"but got {self.width}x{self.height}"
            )
        
        # Calculate frame position to center it
        self.frame_y = (self.height - min_height) // 2
        self.frame_x = (self.width - FRAME_WIDTH) // 2
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # Wins
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Jackpot
        curses.init_pair(3, curses.COLOR_CYAN, -1)    # UI elements
        curses.init_pair(4, curses.COLOR_RED, -1)     # Losses
        
        # Set up screen for animation
        stdscr.nodelay(True)  # Non-blocking input
        curses.curs_set(0)    # Hide cursor    
    def safe_addstr(self, y: int, x: int, text: str, attrs: int = 0) -> None:
        """
        Safely adds a string to the screen, avoiding curses errors
        """
        try:
            screen_y = self.frame_y + y
            screen_x = self.frame_x + x
            
            if 0 <= screen_y < self.height and 0 <= screen_x < self.width:
                max_length = self.width - screen_x
                if len(text) > max_length:
                    text = text[:max_length]
                    
                self.screen.addstr(screen_y, screen_x, text, attrs)
        except curses.error:
            pass
    
    def draw_machine(
        self,
        visible_symbols: List[List[Symbol]],
        last_win: int,
        jackpot: int,
        balance: int,
        bet: int,
        spin_mode: SpinMode,
        spins_remaining: int,
        auto_spinning: bool,
        last_win_text: str = "No wins yet!"
    ) -> None:
        """
        🎨 Draws the complete slot machine display
        """
        try:
            # Only clear the reels area to reduce flickering
            reel_start_y = self.frame_y + 7  # Adjust based on your layout
            reel_height = 5
            for y in range(reel_start_y, reel_start_y + reel_height):
                self.safe_addstr(y, 0, " " * FRAME_WIDTH)
            
            # Draw the main components
            self._draw_frame()
            self._draw_title()
            self._draw_jackpot(jackpot)
            self._draw_reels(visible_symbols)
            self._draw_balance_and_bet(balance, bet)
            self._draw_mode(spin_mode, spins_remaining, auto_spinning)
            self._draw_win_message(last_win_text)
            self._draw_payouts()
            self._draw_controls()
            
            # Refresh only after all drawing is complete
            self.screen.refresh()
        except curses.error as e:
            logging.error(f"Display error: {e}")
    
    def _draw_frame(self) -> None:
        """
        📦 Draws the slot machine's outer frame
        """
        # Top border
        self.safe_addstr(0, 0, "╔" + "═" * (FRAME_WIDTH - 2) + "╗")
        
        # Side borders
        for y in range(1, 24):  # Increased height more
            self.safe_addstr(y, 0, "║")
            self.safe_addstr(y, FRAME_WIDTH - 1, "║")
        
        # Bottom border
        self.safe_addstr(24, 0, "╚" + "═" * (FRAME_WIDTH - 2) + "╝")
    
    def _draw_title(self) -> None:
        """
        🎰 Draws the game title
        """
        title = "🎰 LemDog Slots 🎰"
        x = (FRAME_WIDTH - len(title)) // 2
        self.safe_addstr(1, x, title, curses.color_pair(3) | curses.A_BOLD)
    
    def _draw_jackpot(self, jackpot: int) -> None:
        """
        🏆 Draws the jackpot amount
        """
        jackpot_text = f"🏆 JACKPOT: {jackpot:,} 🏆"
        x = (FRAME_WIDTH - len(jackpot_text)) // 2
        self.safe_addstr(3, x, jackpot_text, curses.color_pair(2))
    
    def _draw_balance_and_bet(self, balance: int, bet: int) -> None:
        """
        💰 Shows balance and bet amounts
        """
        # Format numbers with explicit width to prevent curses display issues
        balance_str = f"{int(balance):<6d}"  # Left-aligned, fixed width of 6
        bet_str = f"{int(bet):<4d}"  # Left-aligned, fixed width of 4
        
        # Only log if this is a new balance value
        if not hasattr(self, '_last_logged_balance') or self._last_logged_balance != balance:
            logging.debug(f"💰 Balance display - Value: {balance}, Formatted: '{balance_str}'")
            self._last_logged_balance = balance
        
        # Create display strings with single emoji and fixed spacing
        balance_text = f"💰 Balance:{balance_str}"  # No space after colon for consistent width
        bet_text = f"🎲 Bet:{bet_str}"  # No space after colon for consistent width
        
        # Calculate positions for better spacing
        balance_x = 8  # Fixed left margin
        bet_x = FRAME_WIDTH - len(bet_text) - 8  # Fixed right margin
        
        # Draw with consistent spacing
        self.safe_addstr(5, balance_x, balance_text)
        self.safe_addstr(5, bet_x, bet_text)
    
    def _draw_mode(self, spin_mode: SpinMode, spins_remaining: int, auto_spinning: bool) -> None:
        """
        🎮 Shows current game mode
        """
        mode_text = f"🍒 Mode: {spin_mode.name}"
        if auto_spinning:
            mode_text += f" ({spins_remaining} spins left)"
        x = (FRAME_WIDTH - len(mode_text)) // 2
        self.safe_addstr(14, x, mode_text, curses.color_pair(3))  # Moved down below win message
    
    def _draw_win_message(self, last_win_text: str) -> None:
        """
        🌟 Shows the last win message
        """
        x = (FRAME_WIDTH - len(last_win_text)) // 2
        self.safe_addstr(12, x, last_win_text, curses.color_pair(1) | curses.A_BOLD)
    
    def _draw_payouts(self) -> None:
        """
        💰 Shows the payout table
        """
        title = "💰 Payouts 💰"
        x = (FRAME_WIDTH - len(title)) // 2
        self.safe_addstr(20, x, title, curses.color_pair(3))
        
        # Define payouts in two rows using correct values from config
        top_row = [
            f"🍒 {PAYOUT_MULTIPLIERS['CHERRY']}x",
            f"🍋 {PAYOUT_MULTIPLIERS['LEMON']}x",
            f"🍊 {PAYOUT_MULTIPLIERS['ORANGE']}x",
            f"🍇 {PAYOUT_MULTIPLIERS['GRAPE']}x"
        ]
        bottom_row = [
            f"💎 {PAYOUT_MULTIPLIERS['DIAMOND']}x",
            f"💰 {PAYOUT_MULTIPLIERS['MONEY']}x",
            f"🎲 {PAYOUT_MULTIPLIERS['DICE']}x",
            f"🌟 {PAYOUT_MULTIPLIERS['STAR']}x"
        ]
        
        y = 21
        
        # Draw top row
        row_text = "   ".join(top_row)
        x = (FRAME_WIDTH - len(row_text)) // 2
        self.safe_addstr(y, x, row_text, curses.color_pair(3))
        
        # Draw bottom row
        row_text = "   ".join(bottom_row)
        x = (FRAME_WIDTH - len(row_text)) // 2
        self.safe_addstr(y + 1, x, row_text, curses.color_pair(3))
    
    def _draw_controls(self) -> None:
        """
        🎮 Shows the game controls
        """
        title = "🎮 Controls 🎮"
        x = (FRAME_WIDTH - len(title)) // 2
        self.safe_addstr(16, x, title, curses.color_pair(3))
        
        controls = [
            "SPACE - Spin/Stop    ↑/↓ - Adjust Bet",
            "←/→ - Change Mode    TAB - View Stats    Q - Quit"
        ]
        
        y = 17
        for text in controls:
            x = (FRAME_WIDTH - len(text)) // 2
            self.safe_addstr(y, x, text, curses.color_pair(3))
            y += 1
        
        # Add extra line break before payouts
        y += 1
    
    def _draw_reels(self, reels: List[List[Symbol]]) -> None:
        """
        🎰 Draws all three reels with their visible symbols
        """
        if not reels:
            return
            
        # Calculate positions
        center_y = 8  # Added one line break after balance/bet
        
        # Calculate spacing for three reels
        symbol_width = 2  # Each emoji is typically 2 characters wide
        total_width = (symbol_width * 3) + (len(SYMBOL_SPACING) * 2)  # 3 reels + 2 spaces between them
        start_x = (FRAME_WIDTH - total_width) // 2
        
        # Draw each reel
        for reel_idx, reel_symbols in enumerate(reels):
            # Calculate x position for this reel
            reel_x = start_x + (reel_idx * (symbol_width + len(SYMBOL_SPACING)))
            
            # Draw symbols for this reel
            for row, symbol in enumerate(reel_symbols):
                y = center_y - 1 + row  # Start one row above center
                self.safe_addstr(y, reel_x, symbol.value)
        
        # Draw payline indicators
        self.safe_addstr(center_y, start_x - 2, "▶")  # Left arrow
        self.safe_addstr(center_y, start_x + total_width + 1, "◀")  # Right arrow

