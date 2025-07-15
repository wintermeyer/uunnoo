# UNO Game Bug Report

After thorough analysis, I've found several critical bugs in the codebase:

## Summary of Fixes Applied in uno_fixed.py:
1. ✅ Fixed UNO penalty to only check player who just played
2. ✅ Added proper deck refill before each draw operation
3. ✅ Fixed UNO call persistence across turns
4. ✅ Added tracking for when player goes to 1 card
5. ✅ Added cards_remaining() method for better deck management

## Detailed Bug Analysis:

## 1. **Critical: UNO Penalty Applied Every Turn** 
**Location**: uno.py:348-350
```python
for player in self.players:
    if len(player.hand) == 1:
        self.check_uno_penalty(player)
```
**Bug**: Checks ALL players every turn, not just the one who just played. If you have 1 card and forget UNO, you get 2 penalty cards EVERY turn.
**Fix**: Only check the player who just reduced their hand to 1 card.

## 2. **Critical: Deck Refill Can Fail**
**Location**: uno.py:324-327
```python
if self.deck.cards and len(self.deck.cards) < 10:
    old_top = self.discard_pile.pop()
    self.deck.add_cards(self.discard_pile)
    self.discard_pile = [old_top]
```
**Bug**: Only refills when < 10 cards, but +4 cards require 4 draws. Could crash if deck has 3 cards and player must draw 4.
**Fix**: Check before EACH draw operation, or refill when cards < max_draw_amount.

## 3. **Major: UNO Call Reset Too Early**
**Location**: uno.py:287
```python
player.reset_uno_call()
```
**Bug**: Resets at turn START. If player calls UNO then draws (no playable card), the call is forgotten.
**Fix**: Reset only after successfully playing a card or after penalty is applied.

## 4. **Major: GUI Can Get Stuck**
**Location**: uno_gui.py:280, 438
```python
self.can_play = False
# ... later
self.root.after(1500, self.computer_turn)
```
**Bug**: If error occurs, `can_play` never returns to True, permanently disabling player actions.
**Fix**: Add try-finally blocks or timeout recovery.

## 5. **Major: UNO Button Never Re-enables**
**Location**: uno_gui.py:474
```python
self.uno_button.config(state=tk.DISABLED)
```
**Bug**: Disabled after use but never re-enabled for next UNO situation.
**Fix**: Re-enable in update_display() when player doesn't have UNO.

## 6. **Major: No Wild Card Color Enforcement**
**Location**: uno_gui.py:358-361
```python
dialog = ColorSelectionDialog(self.root)
self.root.wait_window(dialog)
if dialog.selected_color:
    self.game.declared_color = dialog.selected_color
```
**Bug**: If user closes dialog without selecting, no color is set but game continues.
**Fix**: Force selection or use default color.

## 7. **Moderate: Message Overlap**
**Location**: uno_gui.py:482-483
```python
self.message_label.config(text=message)
self.root.after(3000, lambda: self.message_label.config(text=""))
```
**Bug**: Multiple messages overwrite each other; timers conflict.
**Fix**: Cancel previous timer before setting new message.

## 8. **Moderate: Draw Validation Missing**
**Location**: uno.py:88-92
```python
def draw_card(self, deck: Deck) -> Optional[Card]:
    card = deck.draw()
    if card:
        self.hand.append(card)
    return card
```
**Bug**: No handling when deck is completely empty (even after refill attempt).
**Fix**: Add proper empty deck handling.

## 9. **Minor: Redundant Deck Check**
**Location**: uno.py:324
```python
if self.deck.cards and len(self.deck.cards) < 10:
```
**Bug**: `self.deck.cards` check is redundant with length check.
**Fix**: Use only `if len(self.deck.cards) < 10:`

## 10. **Edge Case: Skip Loop in 2-Player**
**Location**: Game logic
**Bug**: In 2-player game, multiple Skip cards = infinite skip loop.
**Fix**: Add skip counter or special 2-player rules.

## 11. **Edge Case: Color Persistence**
**Location**: Game state management  
**Bug**: `declared_color` only clears when new card played, could persist incorrectly.
**Fix**: Clear after each successful play validation.

## 12. **GUI Race Condition**
**Location**: Computer turn scheduling
**Bug**: Multiple computer turns could be scheduled if player clicks during animation.
**Fix**: Add turn lock or cancel previous scheduled turns.

## Testing Recommendations:
1. Test with minimal deck (force multiple refills)
2. Test UNO penalties with various timing scenarios  
3. Test rapid clicking in GUI version
4. Test 2-player games with multiple skip cards
5. Test closing color dialog without selection
6. Test game with all +4 cards played consecutively

## Most Critical Fixes Needed:
1. **UNO penalty system** - Currently penalizes innocent players
2. **Deck refill logic** - Can crash when drawing many cards
3. **GUI state management** - Can permanently lock player out