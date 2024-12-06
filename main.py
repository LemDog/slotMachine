#!/usr/bin/env python3
"""
LemDog Slots - A beautiful text-based slot machine game.

This is the main entry point for the slot machine game. It handles:
- Command line argument parsing
- Curses initialization and cleanup
- Main game loop and user input processing
- Game state management and display updates

The game features multiple spin modes, statistics tracking, and a user-friendly
text-based interface built with curses.
"""
import argparse
import curses
from typing import Optional

from src.core.enums import SpinMode
from src.core.game import SlotMachine
from src.ui.display import GameDisplay
from src.ui.stats import StatsDisplay
from src.utils.config import MIN_BET, MAX_BET, SCREEN_REFRESH_RATE
from src.utils.logger import setup_debug_logging

def main(stdscr: 'curses.window') -> None:
    """
    Main game loop and initialization.
    
    This function:
    1. Initializes the curses environment and game components
    2. Processes user input and updates game state
    3. Manages the display between game and statistics views
    4. Handles auto-spinning functionality
    
    Args:
        stdscr: The main curses window object for display management
    
    Key Controls:
        - Space: Start/Stop auto-spin
        - Tab: Toggle statistics view
        - ↑/↓: Adjust bet amount
        - ←/→: Change spin mode
        - q: Quit game
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LemDog Slots - A text-based slot machine game')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        setup_debug_logging()

    # Initialize curses
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(SCREEN_REFRESH_RATE)  # Set screen refresh rate
    stdscr.keypad(True)  # Enable special key input

    # Initialize game components
    display = GameDisplay(stdscr)
    game = SlotMachine(display)
    stats_display = StatsDisplay(stdscr)
    show_stats = False

    # Initial screen setup
    stdscr.clear()
    display.draw_machine(
        visible_symbols=game.get_visible_symbols(),
        last_win=game.last_win,
        jackpot=game.jackpot,
        balance=game.balance,
        bet=game.bet,
        spin_mode=game.spin_mode,
        spins_remaining=game.spins_remaining,
        auto_spinning=game.auto_spinning,
        last_win_text=game.last_win_text
    )
    stdscr.refresh()

    while True:
        # Draw current state
        if show_stats:
            stats_display.draw_stats_view(
                frame_y=3,
                spin_history=game.spin_history,
                session_start=game.session_start,
                balance=game.balance,
                starting_balance=game.starting_balance,
                biggest_win=game.biggest_win
            )
            stdscr.refresh()
        else:
            # Only redraw if spinning or after input
            if game.reels.spinning:
                display.draw_machine(
                    visible_symbols=game.get_visible_symbols(),
                    last_win=game.last_win,
                    jackpot=game.jackpot,
                    balance=game.balance,
                    bet=game.bet,
                    spin_mode=game.spin_mode,
                    spins_remaining=game.spins_remaining,
                    auto_spinning=game.auto_spinning,
                    last_win_text=game.last_win_text
                )
                stdscr.refresh()
        
        # Handle auto-spinning
        if game.auto_spinning or game.reels.spinning:
            game.handle_auto_spin()
            continue  # Skip key processing while spinning

        # Handle user input
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1  # No key pressed
            continue

        if key == ord('q'):
            break
        elif key == ord(' '):
            if game.auto_spinning:
                game.stop_auto_spin()
            else:
                game.start_auto_spin()
        elif key == ord('\t'):
            show_stats = not show_stats
            stdscr.clear()  # Clear screen when switching views
            if not show_stats:
                # Redraw game view immediately when switching back
                display.draw_machine(
                    visible_symbols=game.get_visible_symbols(),
                    last_win=game.last_win,
                    jackpot=game.jackpot,
                    balance=game.balance,
                    bet=game.bet,
                    spin_mode=game.spin_mode,
                    spins_remaining=game.spins_remaining,
                    auto_spinning=game.auto_spinning,
                    last_win_text=game.last_win_text
                )
            stdscr.refresh()
        elif key == curses.KEY_UP and not show_stats:
            game.bet = min(MAX_BET, game.bet + 5)
            # Redraw after bet change
            display.draw_machine(
                visible_symbols=game.get_visible_symbols(),
                last_win=game.last_win,
                jackpot=game.jackpot,
                balance=game.balance,
                bet=game.bet,
                spin_mode=game.spin_mode,
                spins_remaining=game.spins_remaining,
                auto_spinning=game.auto_spinning,
                last_win_text=game.last_win_text
            )
            stdscr.refresh()
        elif key == curses.KEY_DOWN and not show_stats:
            game.bet = max(MIN_BET, game.bet - 5)
            # Redraw after bet change
            display.draw_machine(
                visible_symbols=game.get_visible_symbols(),
                last_win=game.last_win,
                jackpot=game.jackpot,
                balance=game.balance,
                bet=game.bet,
                spin_mode=game.spin_mode,
                spins_remaining=game.spins_remaining,
                auto_spinning=game.auto_spinning,
                last_win_text=game.last_win_text
            )
            stdscr.refresh()
        elif key == curses.KEY_RIGHT:
            if show_stats:
                stats_display.handle_input(key)
            else:
                modes = list(SpinMode)
                current_idx = modes.index(game.spin_mode)
                game.spin_mode = modes[(current_idx + 1) % len(modes)]
                # Redraw after mode change
                display.draw_machine(
                    visible_symbols=game.get_visible_symbols(),
                    last_win=game.last_win,
                    jackpot=game.jackpot,
                    balance=game.balance,
                    bet=game.bet,
                    spin_mode=game.spin_mode,
                    spins_remaining=game.spins_remaining,
                    auto_spinning=game.auto_spinning,
                    last_win_text=game.last_win_text
                )
                stdscr.refresh()
        elif key == curses.KEY_LEFT:
            if show_stats:
                stats_display.handle_input(key)
            else:
                modes = list(SpinMode)
                current_idx = modes.index(game.spin_mode)
                game.spin_mode = modes[(current_idx - 1) % len(modes)]
                # Redraw after mode change
                display.draw_machine(
                    visible_symbols=game.get_visible_symbols(),
                    last_win=game.last_win,
                    jackpot=game.jackpot,
                    balance=game.balance,
                    bet=game.bet,
                    spin_mode=game.spin_mode,
                    spins_remaining=game.spins_remaining,
                    auto_spinning=game.auto_spinning,
                    last_win_text=game.last_win_text
                )
                stdscr.refresh()

if __name__ == "__main__":
    # Use curses wrapper for proper initialization and cleanup
    curses.wrapper(main) 