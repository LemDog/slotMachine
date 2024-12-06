"""
📊 Statistics Display - For players who love their numbers!

This module handles the display of game statistics and analytics. It's perfect
for players who want to track their performance and see how lucky they've been! 
Think of it as your personal slot machine dashboard! 📈
"""

import curses
import math
import os
from datetime import datetime
from typing import List, Optional

from src.models.spin_result import SpinResult
from src.utils.config import FRAME_WIDTH, FRAME_HEIGHT, MAX_HISTORY_SIZE

class StatsDisplay:
    """
    📈 Your personal slot machine statistician!
    
    This class creates beautiful statistical displays showing:
    - Win/loss history
    - Session duration
    - Biggest wins
    - Current profit/loss
    - Balance history graph
    - Debug logs
    
    It's like having a tiny accountant inside your slot machine! 🧮
    """
    
    def __init__(self, screen: 'curses.window'):
        """
        📋 Sets up our stats display system
        
        Args:
            screen: The main game window to draw on
        """
        self.screen = screen
        self.height, self.width = screen.getmaxyx()
        self.current_tab = 0  # Start with first tab
        
        # Calculate frame position to center it
        self.frame_y = (self.height - FRAME_HEIGHT) // 2
        self.frame_x = (self.width - FRAME_WIDTH) // 2
        
        # Set up our pretty colors! 🎨
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # 💚 Profits
        curses.init_pair(2, curses.COLOR_RED, -1)     # ❤️ Losses
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # 💛 Highlights
        curses.init_pair(4, curses.COLOR_CYAN, -1)    # 💠 Headers
        
        # Get log file path
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'logs',
            'slot_machine.log'
        )
    
    def safe_addstr(self, y: int, x: int, text: str, attrs: int = 0) -> None:
        """
        🛡️ Safely writes text to the screen
        
        Args:
            y: Vertical position
            x: Horizontal position
            text: Text to write
            attrs: Curses attributes
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
    
    def draw_stats_view(
        self,
        frame_y: int,
        spin_history: List[SpinResult],
        session_start: datetime,
        balance: int,
        starting_balance: int,
        biggest_win: int
    ) -> None:
        """
        📊 Draws the statistics view
        """
        # Clear only the content area to reduce flickering
        for y in range(3, FRAME_HEIGHT - 2):  # Skip frame and tabs
            self.safe_addstr(y, 1, " " * (FRAME_WIDTH - 2))
        
        # Draw frame and tabs (these don't need to be cleared)
        self._draw_frame("📊 Statistics 📊")
        self._draw_tabs()
        
        # Calculate stats
        total_spins = len(spin_history)
        total_won = sum(spin.win_amount for spin in spin_history)
        total_bet = sum(spin.bet_amount for spin in spin_history)
        profit = balance - starting_balance
        win_rate = (sum(1 for spin in spin_history if spin.win_amount > 0) / total_spins * 100
                   if total_spins > 0 else 0)
        
        # Draw content based on current tab
        if self.current_tab == 0:
            self._draw_summary_tab(
                session_start=session_start,
                total_spins=total_spins,
                total_won=total_won,
                total_bet=total_bet,
                profit=profit,
                win_rate=win_rate,
                biggest_win=biggest_win
            )
        elif self.current_tab == 1:
            self.draw_history_tab(
                y=4,  # Start after tabs
                spin_history=spin_history[-8:]  # Show last 8 spins
            )
        elif self.current_tab == 2:
            self._draw_graph_tab(
                frame_y=frame_y,
                spin_history=spin_history,
                starting_balance=starting_balance
            )
        elif self.current_tab == 3:
            self._draw_debug_tab()
        
        # Draw controls at bottom
        self._draw_controls()
        
        # Update screen
        self.screen.refresh()
    
    def _draw_frame(self, title: str) -> None:
        """
        🖼️ Draws a pretty frame around our stats
        """
        # Draw borders
        self.safe_addstr(0, 0, "╔" + "═" * (FRAME_WIDTH - 2) + "╗")
        for y in range(1, FRAME_HEIGHT - 1):
            self.safe_addstr(y, 0, "║")
            self.safe_addstr(y, FRAME_WIDTH - 1, "║")
        self.safe_addstr(FRAME_HEIGHT - 1, 0, "╚" + "═" * (FRAME_WIDTH - 2) + "╝")
        
        # Draw title
        x = (FRAME_WIDTH - len(title)) // 2
        self.safe_addstr(1, x, title, curses.color_pair(4) | curses.A_BOLD)
    
    def _draw_summary_tab(
        self,
        session_start: datetime,
        total_spins: int,
        total_won: int,
        total_bet: int,
        profit: int,
        win_rate: float,
        biggest_win: int
    ) -> None:
        """
        📊 Shows the summary statistics tab
        """
        y = 4  # Start after tabs
        
        # Calculate session duration
        duration = datetime.now() - session_start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        # Show session info
        self.safe_addstr(y, 4, f"⏱️ Session Time: {hours}h {minutes}m")
        y += 2
        
        # Show spin stats
        self.safe_addstr(y, 4, f"🎲 Total Spins: {total_spins}")
        y += 1
        self.safe_addstr(y, 4, f"💰 Total Won: {total_won}")
        y += 1
        self.safe_addstr(y, 4, f"💸 Total Bet: {total_bet}")
        y += 1
        
        # Show profit/loss in appropriate color
        profit_text = f"📈 Profit/Loss: {profit:+}"
        color = curses.color_pair(1) if profit >= 0 else curses.color_pair(4)
        self.safe_addstr(y, 4, profit_text, color)
        y += 2
        
        # Show win rate and biggest win
        self.safe_addstr(y, 4, f"🎯 Win Rate: {win_rate:.1f}%")
        y += 1
        self.safe_addstr(y, 4, f"⭐ Biggest Win: {biggest_win}")
    
    def draw_history_tab(self, y: int, spin_history: List[SpinResult]) -> None:
        """
        📜 Draws the spin history tab
        
        Shows recent spins with:
        - Bet amount
        - Win amount
        - Symbols that landed
        """
        self.safe_addstr(y, 2, "Recent Spins:", curses.color_pair(3))
        y += 2
        
        # Show most recent spins first (up to 8 spins)
        visible_spins = list(reversed(spin_history[-8:]))
        
        for spin in visible_spins:
            # Format bet and win with colors
            if spin.win_amount > 0:
                bet_color = curses.color_pair(1)  # Green for wins
            else:
                bet_color = curses.color_pair(4)  # Red for losses
            
            bet_text = f"Bet: {spin.bet_amount:3d}"
            win_text = f"Win: {spin.win_amount:3d}"
            symbols_text = " ".join(s.value for s in spin.symbols)
            
            # Ensure text fits within frame
            max_width = FRAME_WIDTH - 4  # Leave room for borders
            line_text = f"{bet_text} | {win_text} | {symbols_text}"
            if len(line_text) > max_width:
                line_text = line_text[:max_width-3] + "..."
            
            self.safe_addstr(y, 2, line_text, bet_color)
            y += 1
            
            if y >= FRAME_HEIGHT - 3:  # Leave room for controls
                break
    
    def _draw_graph_tab(
        self,
        frame_y: int,
        spin_history: List[SpinResult],
        starting_balance: int
    ) -> None:
        """
        📈 Shows the balance history graph
        """
        if len(spin_history) < 2:
            self.safe_addstr(4, 2, "Not enough data for graph yet!", curses.color_pair(4))
            return
            
        # Calculate balances for graph
        balances = [starting_balance]
        for spin in spin_history:
            new_balance = balances[-1] - spin.bet_amount + spin.win_amount
            balances.append(new_balance)
        
        # Graph dimensions
        graph_width = FRAME_WIDTH - 12  # Leave room for y-axis labels
        graph_height = 8
        
        # Calculate range with padding
        max_bal = max(balances)
        min_bal = min(balances)
        range_size = max_bal - min_bal
        if range_size == 0:  # Handle flat line case
            range_size = max_bal * 0.2 or 100  # Default to 100 if max_bal is 0
            max_bal += range_size / 2
            min_bal -= range_size / 2
        
        # Add padding
        padding = range_size * 0.1
        max_bal += padding
        min_bal -= padding
        
        # Round to nice numbers
        step = 10 ** (len(str(int(range_size))) - 1)  # Round to nearest power of 10
        min_bal = math.floor(min_bal / step) * step
        max_bal = math.ceil(max_bal / step) * step
        
        # Draw axes
        y_start = 4  # Start after tabs
        x_start = 8  # Leave room for y-axis labels
        
        # Draw y-axis vertical line first
        for i in range(graph_height + 1):
            self.safe_addstr(y_start + i, x_start - 1, "│")
        
        # Draw y-axis labels and ticks
        for i in range(graph_height + 1):
            val = min_bal + (max_bal - min_bal) * (i / graph_height)
            if i % 2 == 0:  # Show every other value
                label = f"{int(val):4d} "
                self.safe_addstr(y_start + graph_height - i, x_start - 6, label)
                self.safe_addstr(y_start + graph_height - i, x_start - 1, "┤")
            else:
                self.safe_addstr(y_start + graph_height - i, x_start - 1, "┤")
        
        # Draw x-axis
        self.safe_addstr(y_start + graph_height, x_start - 1, "└" + "─" * graph_width)
        
        # Plot points with subtle connecting dots
        points = []
        for i, balance in enumerate(balances):
            # Calculate point position
            x = x_start + int((i * (graph_width - 1)) / (len(balances) - 1)) if len(balances) > 1 else x_start
            y = y_start + graph_height - int(((balance - min_bal) * graph_height) / (max_bal - min_bal))
            
            # Ensure y is within bounds
            y = max(y_start, min(y_start + graph_height, y))
            points.append((x, y))
            
            # Draw main point
            self.safe_addstr(y, x, "●", curses.color_pair(3))
            
            # Draw subtle connecting dots if not the last point
            if i < len(balances) - 1:
                next_x = x_start + int(((i + 1) * (graph_width - 1)) / (len(balances) - 1))
                next_y = y_start + graph_height - int(((balances[i + 1] - min_bal) * graph_height) / (max_bal - min_bal))
                next_y = max(y_start, min(y_start + graph_height, next_y))
                
                # Calculate number of dots based on distance
                dx = next_x - x
                dy = next_y - y
                distance = max(abs(dx), abs(dy))
                
                if distance > 1:  # Only if points aren't adjacent
                    # Use fewer dots for longer distances
                    num_dots = min(distance // 2, 5)  # Maximum 5 dots between points
                    
                    for step in range(1, num_dots + 1):
                        progress = step / (num_dots + 1)
                        dot_x = x + int(dx * progress)
                        dot_y = y + int(dy * progress)
                        
                        # Don't draw dots too close to points
                        if abs(dot_x - x) > 1 and abs(dot_x - next_x) > 1:
                            self.safe_addstr(dot_y, dot_x, "·", curses.color_pair(3))
    
    def _draw_tabs(self) -> None:
        """
        📑 Draws the tab headers
        """
        tabs = ["Summary", "History", "Graph", "Debug"]
        x = 2
        y = 2
        
        for i, tab in enumerate(tabs):
            # Highlight current tab
            if i == self.current_tab:
                attrs = curses.A_REVERSE | curses.A_BOLD
            else:
                attrs = 0
                
            self.safe_addstr(y, x, f" {tab} ", attrs)
            x += len(tab) + 3
            
            # Draw separator between tabs
            if i < len(tabs) - 1:
                self.safe_addstr(y, x - 1, "│")
    
    def _draw_debug_tab(self) -> None:
        """
        🐛 Shows the debug log messages
        """
        y = 4  # Start after tabs
        
        try:
            # Read the last 15 lines from the log file
            with open(self.log_file, 'r') as f:
                # Read all lines and get the last 15
                lines = f.readlines()
                messages = lines[-15:] if lines else []
                
                if not messages:
                    self.safe_addstr(y, 2, "No debug messages yet!", curses.color_pair(4))
                    return
                    
                # Draw header
                self.safe_addstr(y, 2, "Recent Debug Messages:", curses.color_pair(4) | curses.A_BOLD)
                y += 2
                
                # Show most recent messages first
                for msg in reversed(messages):
                    msg = msg.strip()  # Remove newlines
                    
                    # Truncate message if too long
                    max_width = FRAME_WIDTH - 4  # Leave room for borders
                    if len(msg) > max_width:
                        msg = msg[:max_width-3] + "..."
                        
                    # Color based on log level
                    color = curses.color_pair(4)  # Default cyan
                    if "ERROR" in msg:
                        color = curses.color_pair(2)  # Red for errors
                    elif "WARNING" in msg:
                        color = curses.color_pair(3)  # Yellow for warnings
                    elif "INFO" in msg:
                        color = curses.color_pair(1)  # Green for info
                        
                    self.safe_addstr(y, 2, msg, color)
                    y += 1
                    
                    if y >= FRAME_HEIGHT - 3:  # Leave room for controls
                        break
                        
        except (IOError, OSError) as e:
            self.safe_addstr(y, 2, f"Could not read debug log: {e}", curses.color_pair(2))
    
    def _draw_controls(self) -> None:
        """
        🎮 Shows the stats view controls
        """
        controls = [
            "←/→: Switch Tab",
            "TAB: Return to Game",
            "Q: Quit"
        ]
        
        # Calculate spacing
        total_width = sum(len(c) for c in controls) + len(controls) - 1
        spacing = (FRAME_WIDTH - total_width) // (len(controls) + 1)
        
        # Draw controls
        x = spacing
        y = FRAME_HEIGHT - 2
        for control in controls:
            self.safe_addstr(y, x, control, curses.color_pair(4))
            x += len(control) + spacing
    
    def _handle_tab_change(self, direction: int) -> None:
        """
        🔄 Changes the current tab
        
        This method handles switching between tabs in the stats view:
        - Summary tab: Shows overall session statistics
        - History tab: Shows recent spins and results
        - Graph tab: Shows balance history chart
        - Debug tab: Shows debug log messages
        
        Args:
            direction: 1 for next tab, -1 for previous tab
        """
        num_tabs = 4  # Summary, History, Graph, Debug
        self.current_tab = (self.current_tab + direction) % num_tabs
    
    def handle_input(self, key: int) -> None:
        """
        🎮 Handles keyboard input for the stats view
        
        Args:
            key: The key that was pressed
        """
        if key == curses.KEY_LEFT:
            self.current_tab = (self.current_tab - 1) % 4  # Now 4 tabs
        elif key == curses.KEY_RIGHT:
            self.current_tab = (self.current_tab + 1) % 4  # Now 4 tabs