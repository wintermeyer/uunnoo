import random
from enum import Enum
from typing import List, Optional, Tuple

class Color(Enum):
    RED = "Rot"
    BLUE = "Blau"
    GREEN = "Grün"
    YELLOW = "Gelb"
    WILD = "Wild"

class CardType(Enum):
    NUMBER = "Zahl"
    SKIP = "Aussetzen"
    REVERSE = "Richtungswechsel"
    DRAW_TWO = "Plus 2"
    WILD = "Farbwahl"
    WILD_DRAW_FOUR = "Plus 4"

class Card:
    def __init__(self, color: Color, card_type: CardType, value: Optional[int] = None):
        self.color = color
        self.card_type = card_type
        self.value = value
    
    def __str__(self):
        if self.card_type == CardType.NUMBER:
            return f"{self.color.value} {self.value}"
        elif self.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return self.card_type.value
        else:
            return f"{self.color.value} {self.card_type.value}"
    
    def can_play_on(self, other: 'Card', declared_color: Optional[Color] = None) -> bool:
        if self.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return True
        
        if declared_color and self.color == declared_color:
            return True
        
        if self.color == other.color:
            return True
        
        if self.card_type == CardType.NUMBER and other.card_type == CardType.NUMBER:
            return self.value == other.value
        
        if self.card_type == other.card_type and self.card_type != CardType.NUMBER:
            return True
        
        return False

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
        self.shuffle()
    
    def _create_deck(self):
        colors = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]
        
        for color in colors:
            self.cards.append(Card(color, CardType.NUMBER, 0))
            
            for value in range(1, 10):
                self.cards.append(Card(color, CardType.NUMBER, value))
                self.cards.append(Card(color, CardType.NUMBER, value))
            
            for _ in range(2):
                self.cards.append(Card(color, CardType.SKIP))
                self.cards.append(Card(color, CardType.REVERSE))
                self.cards.append(Card(color, CardType.DRAW_TWO))
        
        for _ in range(4):
            self.cards.append(Card(Color.WILD, CardType.WILD))
            self.cards.append(Card(Color.WILD, CardType.WILD_DRAW_FOUR))
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        if self.cards:
            return self.cards.pop()
        return None
    
    def add_cards(self, cards: List[Card]):
        self.cards.extend(cards)
        self.shuffle()
    
    def cards_remaining(self) -> int:
        return len(self.cards)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.has_called_uno = False
        self.just_played_second_to_last = False  # FIX: Track when player just went to 1 card
    
    def draw_card(self, deck: Deck) -> Optional[Card]:
        card = deck.draw()
        if card:
            self.hand.append(card)
            # FIX: Reset UNO status when drawing
            if len(self.hand) > 1:
                self.has_called_uno = False
                self.just_played_second_to_last = False
        return card
    
    def play_card(self, index: int) -> Optional[Card]:
        if 0 <= index < len(self.hand):
            # FIX: Track if player is going from 2 cards to 1 card
            if len(self.hand) == 2:
                self.just_played_second_to_last = True
            return self.hand.pop(index)
        return None
    
    def has_uno(self) -> bool:
        return len(self.hand) == 1
    
    def call_uno(self):
        if self.has_uno():
            self.has_called_uno = True
    
    def reset_uno_call(self):
        # FIX: Only reset if player no longer has UNO
        if not self.has_uno():
            self.has_called_uno = False
            self.just_played_second_to_last = False

class HumanPlayer(Player):
    def choose_card(self, top_card: Card, declared_color: Optional[Color] = None) -> Optional[int]:
        print(f"\n{self.name}, deine Karten:")
        playable_indices = []
        
        for i, card in enumerate(self.hand):
            can_play = card.can_play_on(top_card, declared_color)
            print(f"{i + 1}: {card} {'✓' if can_play else '✗'}")
            if can_play:
                playable_indices.append(i)
        
        if not playable_indices:
            print("Keine spielbare Karte. Du musst ziehen.")
            return None
        
        while True:
            try:
                choice = input("Wähle eine Karte (Nummer) oder 0 zum Ziehen: ")
                if choice == "0":
                    return None
                
                index = int(choice) - 1
                if index in playable_indices:
                    return index
                else:
                    print("Diese Karte kannst du nicht spielen!")
            except ValueError:
                print("Ungültige Eingabe!")
    
    def choose_color(self) -> Color:
        print("\nWähle eine Farbe:")
        colors = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]
        for i, color in enumerate(colors):
            print(f"{i + 1}: {color.value}")
        
        while True:
            try:
                choice = int(input("Farbe (1-4): ")) - 1
                if 0 <= choice < 4:
                    return colors[choice]
            except ValueError:
                pass
            print("Ungültige Eingabe!")

class ComputerPlayer(Player):
    def choose_card(self, top_card: Card, declared_color: Optional[Color] = None) -> Optional[int]:
        playable_indices = []
        
        for i, card in enumerate(self.hand):
            if card.can_play_on(top_card, declared_color):
                playable_indices.append(i)
        
        if not playable_indices:
            return None
        
        action_cards = []
        number_cards = []
        wild_cards = []
        
        for index in playable_indices:
            card = self.hand[index]
            if card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                wild_cards.append(index)
            elif card.card_type in [CardType.SKIP, CardType.REVERSE, CardType.DRAW_TWO]:
                action_cards.append(index)
            else:
                number_cards.append(index)
        
        if len(self.hand) <= 3 and wild_cards:
            return random.choice(wild_cards)
        elif action_cards:
            return random.choice(action_cards)
        elif number_cards:
            return random.choice(number_cards)
        else:
            return random.choice(playable_indices)
    
    def choose_color(self) -> Color:
        color_counts = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.YELLOW: 0}
        
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1
        
        max_color = max(color_counts, key=color_counts.get)
        return max_color

class Game:
    def __init__(self):
        self.deck = Deck()
        self.discard_pile: List[Card] = []
        self.players: List[Player] = []
        self.current_player_index = 0
        self.direction = 1
        self.declared_color: Optional[Color] = None
        
    def setup_game(self):
        print("=== UNO Spiel ===")
        self.players.append(HumanPlayer("Spieler"))
        self.players.append(ComputerPlayer("Computer"))
        
        for player in self.players:
            for _ in range(7):
                player.draw_card(self.deck)
        
        first_card = self.deck.draw()
        while first_card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            self.deck.cards.insert(0, first_card)
            self.deck.shuffle()
            first_card = self.deck.draw()
        
        self.discard_pile.append(first_card)
    
    def get_top_card(self) -> Card:
        return self.discard_pile[-1]
    
    def ensure_deck_has_cards(self, needed: int = 1) -> bool:
        """FIX: Ensure deck has enough cards before drawing"""
        if self.deck.cards_remaining() >= needed:
            return True
        
        if len(self.discard_pile) <= 1:
            print("Warnung: Nicht genug Karten im Spiel!")
            return False
        
        # Refill deck from discard pile
        old_top = self.discard_pile.pop()
        self.deck.add_cards(self.discard_pile)
        self.discard_pile = [old_top]
        
        return self.deck.cards_remaining() >= needed
    
    def handle_action_card(self, card: Card, player: Player):
        next_player_index = (self.current_player_index + self.direction) % len(self.players)
        next_player = self.players[next_player_index]
        
        if card.card_type == CardType.SKIP:
            print(f"{next_player.name} setzt aus!")
            self.current_player_index = next_player_index
        
        elif card.card_type == CardType.REVERSE:
            self.direction *= -1
            print("Richtungswechsel!")
        
        elif card.card_type == CardType.DRAW_TWO:
            print(f"{next_player.name} muss 2 Karten ziehen!")
            if self.ensure_deck_has_cards(2):
                for _ in range(2):
                    next_player.draw_card(self.deck)
            self.current_player_index = next_player_index
        
        elif card.card_type == CardType.WILD:
            if isinstance(player, HumanPlayer):
                self.declared_color = player.choose_color()
            else:
                self.declared_color = player.choose_color()
            print(f"Neue Farbe: {self.declared_color.value}")
        
        elif card.card_type == CardType.WILD_DRAW_FOUR:
            if isinstance(player, HumanPlayer):
                self.declared_color = player.choose_color()
            else:
                self.declared_color = player.choose_color()
            print(f"Neue Farbe: {self.declared_color.value}")
            print(f"{next_player.name} muss 4 Karten ziehen!")
            if self.ensure_deck_has_cards(4):
                for _ in range(4):
                    next_player.draw_card(self.deck)
            self.current_player_index = next_player_index
    
    def check_uno_penalty(self, player: Player):
        """FIX: Only penalize if player just played their second-to-last card"""
        if player.has_uno() and not player.has_called_uno and player.just_played_second_to_last:
            print(f"{player.name} hat vergessen UNO zu rufen! 2 Strafkarten!")
            if self.ensure_deck_has_cards(2):
                for _ in range(2):
                    player.draw_card(self.deck)
            player.just_played_second_to_last = False
    
    def play_turn(self):
        player = self.players[self.current_player_index]
        print(f"\n=== {player.name} ist am Zug ===")
        print(f"Oberste Karte: {self.get_top_card()}")
        
        if self.declared_color:
            print(f"Aktuelle Farbe: {self.declared_color.value}")
        
        print(f"{player.name} hat {len(player.hand)} Karten")
        
        # FIX: Don't reset UNO call at start of turn
        # player.reset_uno_call()
        
        card_index = player.choose_card(self.get_top_card(), self.declared_color)
        
        if card_index is None:
            print(f"{player.name} zieht eine Karte")
            if self.ensure_deck_has_cards(1):
                drawn_card = player.draw_card(self.deck)
                
                if drawn_card and drawn_card.can_play_on(self.get_top_card(), self.declared_color):
                    if isinstance(player, HumanPlayer):
                        play_drawn = input("Möchtest du die gezogene Karte spielen? (j/n): ").lower() == 'j'
                    else:
                        play_drawn = True
                    
                    if play_drawn:
                        print(f"{player.name} spielt: {drawn_card}")
                        self.discard_pile.append(drawn_card)
                        self.declared_color = None
                        
                        if drawn_card.card_type != CardType.NUMBER:
                            self.handle_action_card(drawn_card, player)
        else:
            card = player.play_card(card_index)
            print(f"{player.name} spielt: {card}")
            self.discard_pile.append(card)
            self.declared_color = None
            
            # FIX: Check UNO immediately after playing
            if player.has_uno():
                if isinstance(player, HumanPlayer):
                    uno_call = input("UNO rufen? (j/n): ").lower() == 'j'
                    if uno_call:
                        player.call_uno()
                        print(f"{player.name} ruft UNO!")
                else:
                    if random.random() > 0.1:
                        player.call_uno()
                        print(f"{player.name} ruft UNO!")
                
                # FIX: Check penalty immediately for this player only
                self.check_uno_penalty(player)
            else:
                # Reset UNO status when player has more than 1 card
                player.reset_uno_call()
            
            if card.card_type != CardType.NUMBER:
                self.handle_action_card(card, player)
        
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
    
    def check_winner(self) -> Optional[Player]:
        for player in self.players:
            if len(player.hand) == 0:
                return player
        return None
    
    def play(self):
        self.setup_game()
        
        while True:
            self.play_turn()
            
            winner = self.check_winner()
            if winner:
                print(f"\n🎉 {winner.name} hat gewonnen! 🎉")
                break

if __name__ == "__main__":
    game = Game()
    game.play()