# UNO Game

A Python implementation of the classic UNO card game with both console and graphical interfaces.

## Features

- Complete UNO rule implementation
- Console-based gameplay
- Modern GUI with Tkinter
- Visual card history (shows last 3-4 played cards)
- Smart computer opponent
- German language interface

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python)

## How to Play

### GUI Version (Recommended)
```bash
python uno_gui_improved.py
```

### Console Version
```bash
python uno.py
```

### Bug-Fixed Console Version
```bash
python uno_fixed.py
```

## Game Rules

- Match cards by color or number
- Special action cards:
  - **Skip (⊘)**: Next player loses turn
  - **Reverse (↻)**: Reverses play direction
  - **Draw Two (+2)**: Next player draws 2 cards
  - **Wild**: Choose any color
  - **Wild Draw Four (+4)**: Choose color, next player draws 4
- Call "UNO!" when you have one card left
- First player to empty their hand wins

## Controls (GUI)

- **Click** on a playable card to play it
- **ZIEHEN** button to draw a card
- **UNO!** button to call UNO when you have one card
- Color selection dialog appears for wild cards

## Files

- `uno.py` - Original console game
- `uno_fixed.py` - Console game with bug fixes
- `uno_gui_improved.py` - GUI version with card history
- `test_uno.py` - Test suite
- `bug_report.md` - Documented bugs and fixes

## Known Issues

See `bug_report.md` for a comprehensive list of bugs found and fixed in the codebase.