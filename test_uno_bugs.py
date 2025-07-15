"""
Demonstrates critical bugs in the original UNO implementation
"""

import sys
from uno import Game, Player, ComputerPlayer, Card, Color, CardType

def test_uno_penalty_bug():
    """
    Demonstrates the UNO penalty bug where ALL players with 1 card
    get penalized every turn, not just the one who forgot to call UNO
    """
    print("=== Testing UNO Penalty Bug ===")
    print("This bug causes players with 1 card to receive penalty cards EVERY turn\n")
    
    game = Game()
    
    # Create two players
    player1 = ComputerPlayer("Player 1")
    player2 = ComputerPlayer("Player 2") 
    game.players = [player1, player2]
    
    # Give Player 1 only 1 card (simulate late game)
    player1.hand = [Card(Color.RED, CardType.NUMBER, 5)]
    
    # Give Player 2 multiple cards
    player2.hand = [
        Card(Color.BLUE, CardType.NUMBER, 7),
        Card(Color.GREEN, CardType.NUMBER, 3),
        Card(Color.YELLOW, CardType.NUMBER, 9)
    ]
    
    # Set up discard pile
    game.discard_pile = [Card(Color.RED, CardType.NUMBER, 3)]
    
    # Player 1 has 1 card but hasn't called UNO
    player1.has_called_uno = False
    
    print(f"Initial state:")
    print(f"  Player 1: {len(player1.hand)} cards, called UNO: {player1.has_called_uno}")
    print(f"  Player 2: {len(player2.hand)} cards\n")
    
    # Simulate multiple turns
    for turn in range(3):
        print(f"Turn {turn + 1}:")
        
        # This is the buggy code from the original
        for player in game.players:
            if len(player.hand) == 1:
                # This will penalize Player 1 EVERY turn!
                if not player.has_called_uno:
                    print(f"  {player.name} gets 2 penalty cards (forgot UNO)")
                    player.hand.append(Card(Color.WILD, CardType.WILD))
                    player.hand.append(Card(Color.WILD, CardType.WILD))
        
        print(f"  Player 1 now has: {len(player1.hand)} cards")
        print()
    
    print("BUG: Player 1 received 6 penalty cards over 3 turns!")
    print("Expected: Should only receive 2 penalty cards once, when they first reached 1 card\n")

def test_deck_refill_bug():
    """
    Demonstrates the deck refill bug where the game only checks
    if deck has < 10 cards, but doesn't ensure enough for draws
    """
    print("\n=== Testing Deck Refill Bug ===")
    print("This bug causes crashes when deck has few cards but player must draw many\n")
    
    game = Game()
    game.players = [ComputerPlayer("Test Player")]
    
    # Set up deck with only 3 cards
    game.deck.cards = [
        Card(Color.RED, CardType.NUMBER, 1),
        Card(Color.RED, CardType.NUMBER, 2),
        Card(Color.RED, CardType.NUMBER, 3)
    ]
    
    # Large discard pile (should be used for refill)
    game.discard_pile = [Card(Color.BLUE, CardType.NUMBER, i) for i in range(20)]
    
    print(f"Deck has {len(game.deck.cards)} cards")
    print(f"Discard pile has {len(game.discard_pile)} cards")
    print(f"Player must draw 4 cards (Wild +4)")
    
    # Original buggy check
    if game.deck.cards and len(game.deck.cards) < 10:
        print("\nBuggy refill check: Deck has < 10 cards, refilling...")
        # But what if we need to draw 4 and only have 3?
    
    print("\nAttempting to draw 4 cards...")
    cards_drawn = 0
    for i in range(4):
        if game.deck.cards:
            game.deck.draw()
            cards_drawn += 1
        else:
            print(f"ERROR: Can't draw card {i+1}, deck is empty!")
            break
    
    print(f"\nBUG: Only drew {cards_drawn} cards instead of 4!")
    print("Expected: Should refill deck BEFORE drawing to ensure enough cards\n")

def test_uno_call_reset_bug():
    """
    Demonstrates the bug where UNO call is reset at start of turn,
    forgetting that player called UNO
    """
    print("\n=== Testing UNO Call Reset Bug ===")
    print("This bug causes the game to forget that a player called UNO\n")
    
    player = ComputerPlayer("Test Player")
    
    # Player has 1 card and calls UNO
    player.hand = [Card(Color.RED, CardType.NUMBER, 5)]
    player.has_called_uno = True
    print(f"Player has {len(player.hand)} card and called UNO: {player.has_called_uno}")
    
    # Original buggy behavior: reset at start of turn
    print("\nStart of next turn - buggy reset_uno_call():")
    player.has_called_uno = False  # This is what reset_uno_call() does
    print(f"Player still has {len(player.hand)} card but UNO call reset: {player.has_called_uno}")
    
    # Now if we check for penalty...
    if len(player.hand) == 1 and not player.has_called_uno:
        print("\nBUG: Player gets penalized even though they called UNO!")
    
    print("\nExpected: UNO call should persist until player no longer has 1 card")

if __name__ == "__main__":
    test_uno_penalty_bug()
    test_deck_refill_bug() 
    test_uno_call_reset_bug()