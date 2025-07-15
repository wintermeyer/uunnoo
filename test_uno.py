import sys
from io import StringIO
from uno import Game, Card, Color, CardType, Deck, HumanPlayer, ComputerPlayer

def test_card_rules():
    print("=== Testing Card Rules ===")
    
    red_5 = Card(Color.RED, CardType.NUMBER, 5)
    red_7 = Card(Color.RED, CardType.NUMBER, 7)
    blue_5 = Card(Color.BLUE, CardType.NUMBER, 5)
    wild = Card(Color.WILD, CardType.WILD)
    
    print(f"Red 5 on Red 7: {red_5.can_play_on(red_7)}")  # True (same color)
    print(f"Blue 5 on Red 5: {blue_5.can_play_on(red_5)}")  # True (same number)
    print(f"Wild on Red 5: {wild.can_play_on(red_5)}")  # True (wild cards always playable)
    print(f"Blue 5 on Red 7: {blue_5.can_play_on(red_7)}")  # False
    
def test_deck():
    print("\n=== Testing Deck ===")
    deck = Deck()
    print(f"Total cards in deck: {len(deck.cards)}")  # Should be 108
    
    card_counts = {}
    for card in deck.cards:
        key = f"{card.color.value} {card.card_type.value}"
        if card.card_type == CardType.NUMBER:
            key += f" {card.value}"
        card_counts[key] = card_counts.get(key, 0) + 1
    
    print("Card distribution:")
    for card_type, count in sorted(card_counts.items()):
        print(f"  {card_type}: {count}")

def test_game_simulation():
    print("\n=== Simulating Computer vs Computer Game ===")
    
    game = Game()
    game.players.append(ComputerPlayer("Computer 1"))
    game.players.append(ComputerPlayer("Computer 2"))
    
    for player in game.players:
        for _ in range(7):
            player.draw_card(game.deck)
    
    first_card = game.deck.draw()
    while first_card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
        game.deck.cards.insert(0, first_card)
        game.deck.shuffle()
        first_card = game.deck.draw()
    
    game.discard_pile.append(first_card)
    
    turns = 0
    max_turns = 50
    
    print(f"Starting game with top card: {first_card}")
    
    while turns < max_turns:
        player = game.players[game.current_player_index]
        print(f"\nTurn {turns + 1}: {player.name} ({len(player.hand)} cards)")
        print(f"Top card: {game.get_top_card()}")
        
        old_hand_size = len(player.hand)
        game.play_turn()
        new_hand_size = len(player.hand)
        
        if new_hand_size == 0:
            print(f"\n{player.name} wins after {turns + 1} turns!")
            break
        elif new_hand_size < old_hand_size:
            print(f"{player.name} played a card")
        else:
            print(f"{player.name} drew cards")
        
        turns += 1
    
    if turns >= max_turns:
        print(f"\nGame ended after {max_turns} turns (max limit reached)")
        for player in game.players:
            print(f"{player.name}: {len(player.hand)} cards remaining")

if __name__ == "__main__":
    test_card_rules()
    test_deck()
    test_game_simulation()