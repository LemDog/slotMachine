"""
🎮 Main entry point for the slot machine game
"""

import curses
import logging
import sys
import time

from src.core.game import SlotMachine
from src.ui.display import GameDisplay
from src.utils.config import SCREEN_REFRESH_RATE
from src.utils.logging import setup_logging, memory_handler

def main(stdscr: 'curses.window') -> None:
    """
    🎮 Main game loop
    
    Args:
        stdscr: The main curses window
    """
    try:
        # Set up logging before anything else
        setup_logging(debug=True)
        
        # Disable curses echo of input
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        # Set up screen refresh rate
        stdscr.timeout(SCREEN_REFRESH_RATE)
        
        # Initialize display
        display = GameDisplay(stdscr)
        
        # Create game instance with display
        game = SlotMachine(display)
        
        # Main game loop
        while True:
            # Handle input
            key = stdscr.getch()
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                if game.reels.spinning or game.auto_spinning:
                    game.stop_auto_spin()
                else:
                    game.start_auto_spin()
            elif key == curses.KEY_UP:
                game.adjust_bet(10)
            elif key == curses.KEY_DOWN:
                game.adjust_bet(-10)
            elif key == curses.KEY_LEFT:
                game.prev_mode()
            elif key == curses.KEY_RIGHT:
                game.next_mode()
            elif key == ord('\t'):
                game.toggle_stats()
            
            # Update game state
            game.handle_auto_spin()
            
            # Draw current state
            display.draw_machine(
                game.reels.get_visible_symbols(),
                game.last_win,
                game.jackpot,
                game.balance,
                game.bet,
                game.spin_mode,
                game.spins_remaining,
                game.auto_spinning,
                game.last_win_text
            )
            
            # Brief pause to prevent CPU hogging
            time.sleep(0.01)
            
    except Exception as e:
        logging.error(f"Game crashed: {e}")
        raise
    finally:
        # Restore terminal state
        stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

if __name__ == "__main__":
    # Redirect stdout/stderr to prevent them from breaking the UI
    class NullStream:
        def write(self, *args, **kwargs): pass
        def flush(self, *args, **kwargs): pass
    
    sys.stdout = NullStream()
    sys.stderr = NullStream()
    
    curses.wrapper(main) 