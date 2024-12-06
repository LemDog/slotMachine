# LemDog Slots 🎰

A beautiful text-based slot machine game built with Python and curses.

## Features

- 🎮 Interactive text-based UI with colorful symbols
- 💰 Multiple betting options and spin modes
- 📊 Detailed statistics tracking
- 🎵 Sound effects (when enabled)
- 🔄 Auto-spin functionality
- 📈 Session history and performance tracking

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd slotMachine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
python main.py
```

Optional flags:
- `-d` or `--debug`: Enable debug logging

### Controls

- `Space`: Start/Stop auto-spin
- `Tab`: Toggle statistics view
- `↑/↓`: Adjust bet amount
- `←/→`: Change spin mode
- `q`: Quit game

## Project Structure

```
slotMachine/
├── main.py                 # Main entry point
├── src/
│   ├── core/              # Core game logic
│   │   ├── enums.py       # Game enumerations
│   │   ├── game.py        # Main game mechanics
│   │   └── reel.py        # Slot reel logic
│   ├── models/            # Data models
│   │   └── spin_result.py # Spin result class
│   ├── ui/                # User interface
│   │   ├── display.py     # Main game display
│   │   └── stats.py       # Statistics display
│   └── utils/             # Utilities
│       ├── config.py      # Game configuration
│       ├── logger.py      # Logging setup
│       └── sound.py       # Sound effects
└── requirements.txt       # Project dependencies
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)