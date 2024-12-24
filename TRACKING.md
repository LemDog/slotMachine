# 🎰 LemDog Slots - Bug Tracking & Todo List

## 🐛 BUGS

### Critical Issues

1. **Symbol Display Issue**
   - Logs show correct symbols (e.g., "Orange Star Star")
   - Game display shows random characters instead of emoji symbols
   - Affects both main game view and history view
   - Win calculations work correctly, purely a display issue
   - Status: 🔴 Open

2. **Auto-Spin Control Issues**
   - Cannot stop auto-spin mode once started
   - Cannot stop multi-spin (5/10) mode once started
   - Should respond to space bar to stop spinning
   - Spin count indicator doesn't update when stopped
   - Running indicator doesn't clear immediately when stop is pressed
   - Status: 🔴 Open

### Major Issues

3. **Win Display State Issue**
   - "Last Win" message randomly reverts to "No wins yet!"
   - Should persist the last win state until a new spin
   - Affects player's ability to see their wins
   - Status: 🔴 Open

4. **Debug Display Issue**
   - Debug information appearing in game screen
   - Should only go to log file
   - Affects game UI readability
   - Status: 🔴 Open

### Minor Issues

5. **Stats Display Issues**
   - History view affected by symbol display issue
   - Shows incorrect characters for symbols in spin history
   - Status: 🔴 Open

6. **Debug Log Path**
   - Fixed with logging.py update
   - Now creates logs in correct location
   - Status: 🟢 Fixed

## ✅ TODO

### Major Features

1. **Game State Persistence**
   - Save game state between sessions
   - Data to persist:
     * Balance
     * Statistics
     * Spin history
     * Biggest wins
     * Session data
   - Requirements:
     * Implement load/save functionality
     * Choose appropriate file format
     * Determine save file location
     * Handle first-time run scenario
   - Status: 📋 Planned

### Minor Features

2. **Sound Documentation**
   - Create README.md in sound folder
   - Should specify:
     * Required sound files
     * Supported formats (wav, mp3, etc.)
     * Recommended length for each sound
     * Volume requirements
     * Naming conventions
     * Special requirements for win/spin/jackpot sounds
     * Installation/setup instructions
   - Status: 📋 Planned

## 📊 Progress Tracking

- 🔴 Open Bugs: 5
- 🟢 Fixed Bugs: 1
- 📋 Planned Features: 2
- ✅ Completed Features: 0

Last Updated: 2024-12-06 
