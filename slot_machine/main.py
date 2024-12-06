import curses
import random
import time
import logging
import argparse
from collections import Counter, deque
from dataclasses import dataclass
from typing import List
from enum import Enum
import heapq
import math

# Setup logging with conditional debug mode
logger = logging.getLogger('slot_machine')
logger.addHandler(logging.NullHandler())  # Default no logging

def setup_debug_logging():
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('slot_debug.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(fh)

class SpinMode(Enum):
    SINGLE = "Single Spin"
    FIVE = "5 Spins"
    TEN = "10 Spins"
    AUTO = "Auto Spin"

@dataclass
class SpinResult:
    symbols: List[str]
    payout: int
    balance: int
    timestamp: float

# Adjusted Symbols and their payouts
SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "💎", "💰", "🎲", "🌟"]  # "🌟" is the Wild symbol
PAYOUTS = {
    "🍒": 2, "🍋": 3, "🍊": 4, "🍇": 5,
    "💎": 10, "💰": 15, "🎲": 20, "🌟": 50  # "🌟" payout used if three appear without acting as Wilds
}

# Frame and display configurations
FRAME_WIDTH = 13  # Further adjusted for perfect centering
SYMBOL_SPACING = "  "  # Keep double space between symbols
SECTION_TITLE_WIDTH = 17  # Width of "=== XXXXX ===" format

class SlotReel:
    """
    Represents a single slot machine reel.
    """
    def __init__(self, reel_id):
        # Adjusted symbol counts to allow rearrangement without adjacent duplicates
        symbol_counts = {
            "🍒": 5,
            "🍋": 5,
            "🍊": 4,
            "🍇": 3,
            "💎": 3,
            "💰": 2,
            "🎲": 2,
            "🌟": 1  # Wild symbol
        }

        self.reel_id = reel_id  # Initialize reel_id before using it

        # Create the symbols list
        self.symbols = self.rearrange_symbols(symbol_counts)

        self.position = 0
        self.length = len(self.symbols)

        # Verify symbols
        if not self.verify_symbols():
            logger.error(f"Reel {self.reel_id} failed verification.")

    def rearrange_symbols(self, symbol_counts):
        """
        Rearrange symbols so that no two identical symbols are adjacent, including wrap-around.
        """
        # Create a list of all symbols
        symbols = []
        for symbol, count in symbol_counts.items():
            symbols.extend([symbol] * count)
        
        # Try to create a valid arrangement
        max_attempts = 1000
        for _ in range(max_attempts):
            random.shuffle(symbols)
            valid = True
            
            # Check each position, including wrap-around
            for i in range(len(symbols)):
                next_idx = (i + 1) % len(symbols)
                if symbols[i] == symbols[next_idx]:
                    valid = False
                    break
            
            if valid:
                return symbols
        
        # If we couldn't find a valid arrangement after max attempts,
        # manually fix any adjacent duplicates
        for i in range(len(symbols)):
            next_idx = (i + 1) % len(symbols)
            if symbols[i] == symbols[next_idx]:
                # Try to swap with a non-adjacent symbol
                for j in range(len(symbols)):
                    if j != i and j != next_idx and j != (next_idx + 1) % len(symbols):
                        if symbols[j] != symbols[i] and symbols[j] != symbols[(next_idx + 1) % len(symbols)]:
                            symbols[next_idx], symbols[j] = symbols[j], symbols[next_idx]
                            break
        
        return symbols

    def rotate(self):
        """
        Rotate the reel by one position.
        """
        self.position = (self.position + 1) % self.length

    def verify_symbols(self):
        """
        Verify that the reel has the correct symbol counts.
        """
        current_counts = Counter(self.symbols)
        expected_counts = {
            "🍒": 5,
            "🍋": 5,
            "🍊": 4,
            "🍇": 3,
            "💎": 3,
            "💰": 2,
            "🎲": 2,
            "🌟": 1
        }
        if current_counts != expected_counts:
            logger.error(f"Reel {self.reel_id} symbol counts mismatch.")
            return False
        return True

    def get_visible_symbols(self):
        """
        Get the three visible symbols (above, current, below).
        """
        symbols = []
        for offset in range(-1, 2):
            idx = (self.position + offset) % self.length
            symbol = self.symbols[idx]
            symbols.append(symbol)
        return symbols

class SlotMachine:
    """
    Represents the slot machine game logic and UI.
    """
    def __init__(self, screen):
        self.screen = screen
        self.balance = 1000
        self.starting_balance = self.balance
        self.bet = 10
        self.jackpot = 1000  # Initialize the jackpot

        # Initialize reels
        self.reels = [SlotReel(i) for i in range(3)]

        self.height, self.width = screen.getmaxyx()
        self.symbol_counts = Counter()
        self.spin_history = deque(maxlen=30)
        self.balance_history = [self.starting_balance]
        self.last_win = None
        self.show_stats = False
        self.stats_tab = 0  # 0 for Stats, 1 for Charts
        self.spin_mode = SpinMode.SINGLE
        self.spins_remaining = 0
        self.auto_spinning = False
        self.biggest_win = None
        self.session_start = time.time()
        self.left_margin = None
        self.next_auto_spin_time = 0  # For controlling auto-spin timing

    def calculate_margins(self):
        """
        Calculate the left margin for aligned text.
        """
        center = self.width // 2
        self.left_margin = center - 9  # Adjusted from -8 to -9 for text alignment

    def draw_centered(self, y, text, align="center"):
        """
        Draw text at the specified y position with proper alignment.
        """
        try:
            text = text.replace("┃", "").strip()
            if self.left_margin is None:
                self.calculate_margins()

            if align == "center":
                x = max(0, (self.width - len(text)) // 2)
            else:  # left align with offset from center
                x = self.left_margin

            self.screen.addstr(y, x, text)
        except curses.error:
            # Silently handle drawing errors
            pass

    def spin(self):
        """
        Perform the actual spinning animation and return winnings.
        """
        # Keep current positions and continue spinning from there
        self.screen.nodelay(True)  # Set non-blocking input

        for reel_idx in range(3):
            spins = 20 + (reel_idx * 8)

            for _ in range(spins):
                # Check for user input to stop auto-spin
                key = self.screen.getch()
                if key == ord(' '):
                    self.auto_spinning = False
                    # Update the screen immediately
                    self.draw_machine()
                    self.screen.refresh()

                self.reels[reel_idx].rotate()
                if random.random() < 0.3:
                    self.reels[reel_idx].rotate()

                self.draw_machine()
                self.screen.refresh()
                time.sleep(0.05)

            # Gradually slow down
            for i in range(5):
                # Check for user input to stop auto-spin
                key = self.screen.getch()
                if key == ord(' '):
                    self.auto_spinning = False
                    # Update the screen immediately
                    self.draw_machine()
                    self.screen.refresh()

                self.reels[reel_idx].rotate()
                self.draw_machine()
                self.screen.refresh()
                time.sleep(0.1 + (i * 0.05))

        # Turn off nodelay
        self.screen.nodelay(False)

        # Record spin result
        middle_symbols = [reel.get_visible_symbols()[1] for reel in self.reels]

        # Implement Near Misses
        if not self.check_win(middle_symbols) and random.random() < 0.2:
            # 20% chance to create a near miss
            middle_symbols = self.create_near_miss(middle_symbols)

        winnings = self.check_win(middle_symbols)

        spin_result = SpinResult(
            symbols=middle_symbols,
            payout=winnings,
            balance=self.balance,
            timestamp=time.time()
        )
        self.spin_history.append(spin_result)
        self.balance_history.append(self.balance)

        if winnings > 0:
            self.last_win = spin_result

        return winnings

    def create_near_miss(self, symbols):
        """
        Adjust symbols to create a near miss scenario without introducing adjacent duplicates.
        """
        # Attempt to adjust one symbol to create a near miss without adjacent duplicates
        idx_to_change = random.choice([0, 1, 2])
        other_idxs = [i for i in [0, 1, 2] if i != idx_to_change]
        target_symbol = symbols[other_idxs[0]]

        reel = self.reels[idx_to_change]
        original_position = reel.position

        # Try shifting the reel to create a near miss
        for offset in [1, -1]:
            new_position = (original_position + offset) % reel.length
            new_symbol = reel.symbols[new_position]

            # Ensure the new symbol is not the same as adjacent symbols
            prev_idx = (new_position - 1) % reel.length
            next_idx = (new_position + 1) % reel.length
            if (reel.symbols[prev_idx] != new_symbol and
                reel.symbols[next_idx] != new_symbol and
                new_symbol == target_symbol):
                reel.position = new_position
                symbols[idx_to_change] = new_symbol
                return symbols

        # If unable to create a near miss without adjacent duplicates, return original symbols
        return symbols

    def draw_machine(self):
        """
        Draw the slot machine interface.
        """
        self.screen.clear()

        try:
            # Initialize colors
            curses.start_color()
            curses.init_pair(1, curses.COLOR_YELLOW, -1)  # For Wild symbol
            curses.init_pair(2, curses.COLOR_GREEN, -1)   # For jackpot amount
            curses.init_pair(3, curses.COLOR_RED, -1)     # For losses
            curses.init_pair(4, curses.COLOR_CYAN, -1)    # For wins
            curses.init_pair(5, curses.COLOR_MAGENTA, -1) # For titles

            # Calculate center once
            center_x = self.width // 2

            # Title
            title = "🐕 LEMDOG SLOTS 🎲"
            title_x = center_x - (len(title) // 2)
            self.screen.addstr(1, title_x, title, curses.color_pair(5))

            if self.show_stats:
                self.draw_stats_view(3)
                return

            frame_y = 3

            # Calculate frame position to center it
            frame_x = center_x - ((FRAME_WIDTH + 2) // 2)  # +2 for border chars

            # Draw frame borders
            self.screen.addstr(frame_y, frame_x, "┏" + "━" * FRAME_WIDTH + "┓")
            self.screen.addstr(frame_y + 4, frame_x, "┗" + "━" * FRAME_WIDTH + "┛")

            # Draw each row with content
            for row in range(3):
                symbols = [reel.get_visible_symbols()[row] for reel in self.reels]
                symbol_display = SYMBOL_SPACING.join(symbols)
                content_width = len(symbol_display)
                total_space = FRAME_WIDTH - content_width
                
                # Calculate padding with slight bias to the right for visual balance
                left_padding = (total_space - 1) // 2
                right_padding = total_space - left_padding

                # Draw left border, content, and right border separately
                self.screen.addstr(frame_y + row + 1, frame_x, "┃")
                content = f"{' ' * left_padding}{symbol_display}{' ' * right_padding}"
                self.screen.addstr(frame_y + row + 1, frame_x + 1, content)
                self.screen.addstr(frame_y + row + 1, frame_x + FRAME_WIDTH + 1, "┃")

                # For middle row, draw arrows outside the frame
                if row == 1:
                    self.screen.addstr(frame_y + row + 1, frame_x - 1, "▶")
                    self.screen.addstr(frame_y + row + 1, frame_x + FRAME_WIDTH + 2, "◀")

            # Draw last win
            if self.last_win:
                win_symbols = " ".join(self.last_win.symbols)
                self.draw_centered(frame_y + 5, f"Last Win: {win_symbols} ${self.last_win.payout}")
            else:
                self.draw_centered(frame_y + 5, "No wins yet!")

            # Stats and mode - shifted right
            self.draw_centered(frame_y + 7, f"Jackpot: ${self.jackpot}", "left")
            self.draw_centered(frame_y + 8, f"Balance: ${self.balance}", "left")
            self.draw_centered(frame_y + 9, f"Current Bet: ${self.bet}", "left")

            # Mode display
            mode_text = f"Mode: {self.spin_mode.value}"
            if self.spin_mode == SpinMode.AUTO and self.auto_spinning:
                mode_text += " (RUNNING)"
            elif self.spins_remaining > 0:
                mode_text += f" ({self.spins_remaining} left)"
            self.draw_centered(frame_y + 10, mode_text, "left")

            # Section titles and controls
            title_x = center_x - (SECTION_TITLE_WIDTH // 2)
            try:
                self.screen.addstr(frame_y + 12, title_x, "=== CONTROLS ===")

                # Controls - shifted right
                self.draw_centered(frame_y + 13, "SPACE - Spin/Stop Auto", "left")
                self.draw_centered(frame_y + 14, "↑/↓ - Adjust Bet", "left")
                self.draw_centered(frame_y + 15, "←/→ - Change Mode", "left")
                self.draw_centered(frame_y + 16, "TAB - Toggle Stats", "left")
                self.draw_centered(frame_y + 17, "Q - Quit", "left")

                # Payouts section
                self.screen.addstr(frame_y + 19, title_x, "=== PAYOUTS ===")

                # Payouts
                payout_str = "  ".join(f"{s}:{PAYOUTS[s]}x" for s in SYMBOLS[:4])
                self.draw_centered(frame_y + 20, payout_str)
                payout_str = "  ".join(f"{s}:{PAYOUTS[s]}x" for s in SYMBOLS[4:])
                self.draw_centered(frame_y + 21, payout_str)
            except curses.error:
                # If we can't draw everything, at least show the game
                pass
        except curses.error:
            # Handle terminal too small for even basic display
            try:
                self.screen.addstr(0, 0, "Terminal too small!")
            except curses.error:
                pass

    def format_time(self, seconds):
        """
        Format time in seconds to hours and minutes.
        """
        minutes = int(seconds // 60)
        hours = minutes // 60
        if hours > 0:
            return f"{hours}h {minutes % 60}m"
        return f"{minutes % 60}m"

    def perform_spin(self):
        """
        Handle a single spin including bet deduction and win processing.
        """
        if self.balance < self.bet:
            return False

        self.balance -= self.bet
        self.jackpot += 1  # Increase jackpot by 1 unit per spin
        winnings = self.spin()

        if winnings > 0:
            if not self.biggest_win or winnings > self.biggest_win.payout:
                self.biggest_win = self.last_win

        return True

    def check_win(self, middle_symbols):
        """
        Check if the middle row symbols constitute a win, considering Wild symbols.
        """
        # Check for jackpot win (three "🌟" symbols)
        if all(s == "🌟" for s in middle_symbols):
            winnings = self.jackpot
            self.balance += winnings
            self.jackpot = 1000  # Reset the jackpot
            return winnings

        # First, find the non-wild symbols in the middle row
        non_wild_symbols = [s for s in middle_symbols if s != "🌟"]

        if not non_wild_symbols:
            # All symbols are Wilds; use highest payout
            actual_symbol = "💰"  # Highest paying regular symbol
        else:
            # Use the most common non-wild symbol
            actual_symbol = max(set(non_wild_symbols), key=non_wild_symbols.count)

        # Check if all symbols are the same when considering Wilds
        if all(s == actual_symbol or s == "🌟" for s in middle_symbols):
            winnings = self.bet * PAYOUTS.get(actual_symbol, 0)
            self.balance += winnings
            return winnings
        else:
            return 0

    def handle_auto_spin(self):
        """
        Handle automatic spinning based on current mode.
        """
        if not self.auto_spinning:
            return

        current_time = time.time()
        if current_time >= self.next_auto_spin_time:
            if self.balance < self.bet:
                self.auto_spinning = False
                self.spins_remaining = 0
                return

            # Perform the spin
            success = self.perform_spin()
            
            if success:
                # Set the next spin time
                self.next_auto_spin_time = current_time + 1.5
                
                # For multi-spin modes, check if we should stop
                if self.spin_mode != SpinMode.AUTO:
                    self.spins_remaining -= 1
                    if self.spins_remaining <= 0:
                        self.auto_spinning = False
            else:
                # If spin failed (e.g., not enough balance)
                self.auto_spinning = False
                self.spins_remaining = 0

            # Force a redraw and refresh after each spin
            self.draw_machine()
            self.screen.refresh()

    def start_auto_spin(self):
        """
        Start auto-spinning based on current mode.
        """
        if self.balance < self.bet:
            return

        # Handle single spin mode
        if self.spin_mode == SpinMode.SINGLE:
            self.perform_spin()
            return

        # Initialize auto-spinning
        self.auto_spinning = True
        self.next_auto_spin_time = time.time()  # Set initial spin time
        
        # Set up spin counts
        if self.spin_mode == SpinMode.FIVE:
            self.spins_remaining = 5
        elif self.spin_mode == SpinMode.TEN:
            self.spins_remaining = 10
        else:  # SpinMode.AUTO
            self.spins_remaining = -1  # Use -1 to indicate infinite spins

        # Perform first spin immediately
        success = self.perform_spin()
        if success:
            if self.spin_mode != SpinMode.AUTO:
                self.spins_remaining -= 1
            self.next_auto_spin_time = time.time() + 1.5
        else:
            self.auto_spinning = False
            self.spins_remaining = 0

    def draw_stats_view(self, frame_y):
        """
        Draw the statistics view including spin history and balance graph.
        """
        # Draw stats title
        title = "Stats for Nerds"
        title_x = self.width // 2 - (len(title) // 2)
        self.screen.addstr(1, title_x, title, curses.color_pair(5))

        # Draw tabs
        tabs_y = 3
        tab_width = 20
        center_x = self.width // 2
        stats_tab = "[Stats]" if self.stats_tab == 0 else " Stats "
        charts_tab = "[Charts]" if self.stats_tab == 1 else " Charts "
        
        # Calculate positions for centered tabs
        total_width = len(stats_tab) + len(charts_tab) + 2  # +2 for spacing
        start_x = center_x - (total_width // 2)
        
        # Draw tabs with appropriate highlighting
        self.screen.addstr(tabs_y, start_x, stats_tab, 
                          curses.A_REVERSE if self.stats_tab == 0 else curses.A_NORMAL)
        self.screen.addstr(tabs_y, start_x + len(stats_tab) + 2, charts_tab,
                          curses.A_REVERSE if self.stats_tab == 1 else curses.A_NORMAL)

        if self.stats_tab == 0:
            # Draw Stats tab content
            self.draw_centered(tabs_y + 2, "=== SPIN HISTORY ===")

            # Show last 10 spins
            history = list(self.spin_history)[-10:]
            if not history:
                self.draw_centered(tabs_y + 4, "No spins yet!")
            else:
                for i, spin in enumerate(history):
                    symbols_str = " ".join(spin.symbols)
                    result_str = f"Win: ${spin.payout}" if spin.payout > 0 else "No win"
                    self.draw_centered(tabs_y + 4 + i, f"{symbols_str} - {result_str}")

            # Session stats
            stats_y = tabs_y + 15
            self.draw_centered(stats_y, "=== SESSION STATS ===")
            session_time = time.time() - self.session_start
            total_spins = len(self.spin_history)
            wins = sum(1 for spin in self.spin_history if spin.payout > 0)
            win_rate = (wins / total_spins * 100) if total_spins > 0 else 0
            profit = self.balance - self.starting_balance

            self.draw_centered(stats_y + 1, f"Time: {self.format_time(session_time)}")
            self.draw_centered(stats_y + 2, f"Spins: {total_spins}")
            self.draw_centered(stats_y + 3, f"Win Rate: {win_rate:.1f}%")
            self.draw_centered(stats_y + 4, f"Profit: ${profit}")
            if self.biggest_win:
                big_win = " ".join(self.biggest_win.symbols)
                self.draw_centered(stats_y + 5, f"Biggest Win: {big_win} ${self.biggest_win.payout}")

        else:
            # Draw Charts tab content
            self.draw_centered(tabs_y + 2, "=== BALANCE HISTORY ===")

            # Draw balance graph
            if len(self.balance_history) > 1:
                # Get the last 30 balances
                balances = self.balance_history[-30:]
                graph_width = 30
                graph_height = 15  # Increased height for better visibility

                # Calculate range with padding
                max_bal = max(balances)
                min_bal = min(balances)
                if max_bal == min_bal:
                    max_bal += 100  # Avoid division by zero and give some range
                    min_bal -= 100
                padding = (max_bal - min_bal) * 0.1
                max_bal += padding
                min_bal -= padding

                # Round min/max to nearest 100
                min_bal = math.floor(min_bal / 100) * 100
                max_bal = math.ceil(max_bal / 100) * 100

                # Draw Y axis
                y_axis_x = tabs_y + 4
                for i in range(graph_height + 1):
                    val = min_bal + (max_bal - min_bal) * (i / graph_height)
                    if i % 3 == 0:  # Show every third value
                        label = f"${val:4.0f} |"
                        self.screen.addstr(tabs_y + 4 + graph_height - i, y_axis_x, label)
                    else:
                        self.screen.addstr(tabs_y + 4 + graph_height - i, y_axis_x + 6, "|")

                # Draw X axis
                x_axis_y = tabs_y + 4 + graph_height
                x_axis = "+" + "-" * (graph_width + 2) + "> Spins"
                self.screen.addstr(x_axis_y, y_axis_x + 6, x_axis)

                # Plot points and lines
                points = []
                for i, balance in enumerate(balances):
                    x = y_axis_x + 7 + int((i / len(balances)) * graph_width)
                    y = tabs_y + 4 + graph_height - int(((balance - min_bal) / (max_bal - min_bal)) * graph_height)
                    points.append((x, y))
                    
                    # Plot point
                    self.screen.addstr(y, x, "*")
                    
                    # Draw lines between points
                    if i > 0:
                        # Draw lines between points using simple characters
                        prev_x, prev_y = points[i-1]
                        if prev_y == y:
                            for x_pos in range(prev_x + 1, x):
                                self.screen.addstr(y, x_pos, "-")
                        elif prev_x == x:
                            for y_pos in range(min(prev_y, y) + 1, max(prev_y, y)):
                                self.screen.addstr(y_pos, x, "|")
                        else:
                            # Simple diagonal line
                            if abs(prev_y - y) == abs(prev_x - x):
                                for j in range(1, abs(prev_x - x)):
                                    y_pos = prev_y + j * (1 if y > prev_y else -1)
                                    x_pos = prev_x + j
                                    self.screen.addstr(y_pos, x_pos, "/" if y < prev_y else "\\")

                # Show spin numbers on X axis
                for i in range(0, len(balances), 5):  # Show every 5th spin
                    x = y_axis_x + 7 + int((i / len(balances)) * graph_width)
                    self.screen.addstr(x_axis_y + 1, x, str(i))

def main(stdscr):
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        setup_debug_logging()

    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.timeout(50)  # Adjusted timeout for smoother auto-spin
    stdscr.keypad(True)  # Enable keypad for arrow keys

    slot_machine = SlotMachine(stdscr)

    while True:
        # Draw current state first
        slot_machine.draw_machine()
        
        # Handle auto-spinning
        if slot_machine.auto_spinning:
            slot_machine.handle_auto_spin()
            # Ensure screen updates for next spin
            stdscr.refresh()
            continue  # Skip key processing while auto-spinning

        try:
            key = stdscr.getch()
        except curses.error:
            key = -1  # No key pressed

        if key == ord('q'):
            break
        elif key == ord(' '):
            if slot_machine.auto_spinning:
                slot_machine.auto_spinning = False
                slot_machine.spins_remaining = 0
            else:
                slot_machine.start_auto_spin()
        elif key == ord('\t'):
            slot_machine.show_stats = not slot_machine.show_stats
            slot_machine.stats_tab = 0  # Reset to first tab when opening stats
        elif key == curses.KEY_UP:
            if not slot_machine.show_stats:
                slot_machine.bet = min(100, slot_machine.bet + 5)
        elif key == curses.KEY_DOWN:
            if not slot_machine.show_stats:
                slot_machine.bet = max(5, slot_machine.bet - 5)
        elif key == curses.KEY_RIGHT:
            if slot_machine.show_stats:
                slot_machine.stats_tab = (slot_machine.stats_tab + 1) % 2
            else:
                modes = list(SpinMode)
                current_idx = modes.index(slot_machine.spin_mode)
                slot_machine.spin_mode = modes[(current_idx + 1) % len(modes)]
        elif key == curses.KEY_LEFT:
            if slot_machine.show_stats:
                slot_machine.stats_tab = (slot_machine.stats_tab - 1) % 2
            else:
                modes = list(SpinMode)
                current_idx = modes.index(slot_machine.spin_mode)
                slot_machine.spin_mode = modes[(current_idx - 1) % len(modes)]

        # Update screen
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)