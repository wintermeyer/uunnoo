import tkinter as tk
from tkinter import messagebox, font as tkfont
import random
from uno import Game, Card, Color, CardType, Deck, Player, HumanPlayer, ComputerPlayer

class CardWidget(tk.Frame):
    def __init__(self, parent, card, clickable=False, click_callback=None, scale=1.0):
        super().__init__(parent, relief=tk.RAISED, borderwidth=2)
        self.card = card
        self.click_callback = click_callback
        
        # Scale dimensions for history cards
        width = int(80 * scale)
        height = int(120 * scale)
        font_size = int(36 * scale) if card.card_type == CardType.NUMBER else int(20 * scale)
        
        color_map = {
            Color.RED: "#FF0000",
            Color.BLUE: "#0000FF",
            Color.GREEN: "#00AA00",
            Color.YELLOW: "#FFD700",
            Color.WILD: "#808080"
        }
        
        bg_color = color_map.get(card.color, "#808080")
        fg_color = "white" if card.color in [Color.BLUE, Color.GREEN, Color.WILD] else "black"
        
        self.configure(bg=bg_color, width=width, height=height)
        self.pack_propagate(False)
        
        if card.card_type == CardType.NUMBER:
            text = str(card.value)
        elif card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            text = "WILD" if card.card_type == CardType.WILD else "+4"
        else:
            text_map = {
                CardType.SKIP: "⊘",
                CardType.REVERSE: "↻",
                CardType.DRAW_TWO: "+2"
            }
            text = text_map.get(card.card_type, "?")
        
        label = tk.Label(self, text=text, bg=bg_color, fg=fg_color,
                        font=("Arial", font_size, "bold"))
        label.pack(expand=True)
        
        if clickable and click_callback:
            self.bind("<Button-1>", lambda e: click_callback(card))
            label.bind("<Button-1>", lambda e: click_callback(card))
            self.bind("<Enter>", lambda e: self.configure(relief=tk.GROOVE))
            self.bind("<Leave>", lambda e: self.configure(relief=tk.RAISED))

class ColorSelectionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Wähle eine Farbe")
        self.selected_color = None
        self.transient(parent)
        self.grab_set()
        
        self.geometry("300x200")
        
        # Make dialog non-closable without selection
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        label = tk.Label(self, text="Wähle eine neue Farbe:", font=("Arial", 14))
        label.pack(pady=10)
        
        colors = [
            (Color.RED, "Rot", "#FF0000"),
            (Color.BLUE, "Blau", "#0000FF"),
            (Color.GREEN, "Grün", "#00AA00"),
            (Color.YELLOW, "Gelb", "#FFD700")
        ]
        
        for color, name, hex_color in colors:
            btn = tk.Button(self, text=name, bg=hex_color, 
                           fg="white" if color in [Color.BLUE, Color.GREEN] else "black",
                           width=15, height=2, font=("Arial", 12, "bold"),
                           command=lambda c=color: self.select_color(c))
            btn.pack(pady=5)
    
    def select_color(self, color):
        self.selected_color = color
        self.destroy()

class UnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNO Spiel")
        self.root.geometry("1200x800")
        self.root.configure(bg="#006400")
        
        self.game = None
        self.player_card_frames = []
        self.selected_card = None
        self.can_play = True
        self.message_timer = None
        
        self.setup_ui()
        self.new_game()
    
    def setup_ui(self):
        self.title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.normal_font = tkfont.Font(family="Arial", size=12)
        
        title_frame = tk.Frame(self.root, bg="#006400")
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        title_label = tk.Label(title_frame, text="UNO", font=self.title_font,
                              bg="#006400", fg="white")
        title_label.pack()
        
        self.status_label = tk.Label(title_frame, text="", font=self.normal_font,
                                    bg="#006400", fg="white")
        self.status_label.pack()
        
        self.computer_frame = tk.Frame(self.root, bg="#006400", height=150)
        self.computer_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.computer_frame.pack_propagate(False)
        
        self.computer_info = tk.Label(self.computer_frame, text="Computer: 7 Karten",
                                     font=("Arial", 16), bg="#006400", fg="white")
        self.computer_info.pack()
        
        self.computer_cards_frame = tk.Frame(self.computer_frame, bg="#006400")
        self.computer_cards_frame.pack(pady=10)
        
        middle_frame = tk.Frame(self.root, bg="#006400", height=200)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        self.draw_pile_frame = tk.Frame(middle_frame, bg="#006400")
        self.draw_pile_frame.pack(side=tk.LEFT, padx=50)
        
        tk.Label(self.draw_pile_frame, text="Nachziehstapel", 
                font=("Arial", 14), bg="#006400", fg="white").pack()
        
        self.draw_button = tk.Button(self.draw_pile_frame, text="ZIEHEN",
                                    bg="#333333", fg="white", width=10, height=6,
                                    font=("Arial", 16, "bold"),
                                    command=self.draw_card)
        self.draw_button.pack(pady=10)
        
        # New: Discard pile with history
        discard_container = tk.Frame(middle_frame, bg="#006400")
        discard_container.pack(side=tk.LEFT, padx=50)
        
        tk.Label(discard_container, text="Ablagestapel",
                font=("Arial", 14), bg="#006400", fg="white").pack()
        
        # Frame for card history
        self.history_frame = tk.Frame(discard_container, bg="#006400")
        self.history_frame.pack(pady=10)
        
        # Subframe for historical cards (stacked)
        self.history_cards_frame = tk.Frame(self.history_frame, bg="#006400")
        self.history_cards_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Arrow to show direction
        self.arrow_label = tk.Label(self.history_frame, text="→", 
                                   font=("Arial", 24), bg="#006400", fg="white")
        self.arrow_label.pack(side=tk.LEFT, padx=10)
        
        # Current card frame
        self.discard_pile_widget = tk.Frame(self.history_frame, bg="#006400")
        self.discard_pile_widget.pack(side=tk.LEFT)
        
        self.color_indicator = tk.Label(discard_container, text="",
                                       font=("Arial", 12), bg="#006400", fg="white")
        self.color_indicator.pack()
        
        control_frame = tk.Frame(middle_frame, bg="#006400")
        control_frame.pack(side=tk.RIGHT, padx=50)
        
        self.uno_button = tk.Button(control_frame, text="UNO!",
                                   bg="#FF0000", fg="white", width=10, height=3,
                                   font=("Arial", 20, "bold"),
                                   command=self.call_uno)
        self.uno_button.pack(pady=10)
        
        self.message_label = tk.Label(control_frame, text="", wraplength=200,
                                     font=("Arial", 12), bg="#006400", fg="yellow")
        self.message_label.pack(pady=10)
        
        self.player_frame = tk.Frame(self.root, bg="#006400", height=150)
        self.player_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        tk.Label(self.player_frame, text="Deine Karten:",
                font=("Arial", 16), bg="#006400", fg="white").pack()
        
        self.player_cards_frame = tk.Frame(self.player_frame, bg="#006400")
        self.player_cards_frame.pack(pady=10)
    
    def new_game(self):
        self.game = Game()
        self.game.players = [
            HumanPlayer("Spieler"),
            ComputerPlayer("Computer")
        ]
        
        for player in self.game.players:
            for _ in range(7):
                player.draw_card(self.game.deck)
        
        first_card = self.game.deck.draw()
        while first_card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            self.game.deck.cards.insert(0, first_card)
            self.game.deck.shuffle()
            first_card = self.game.deck.draw()
        
        self.game.discard_pile.append(first_card)
        
        self.update_display()
        self.show_message("Neues Spiel gestartet!")
    
    def update_display(self):
        for widget in self.computer_cards_frame.winfo_children():
            widget.destroy()
        
        computer = self.game.players[1]
        self.computer_info.config(text=f"Computer: {len(computer.hand)} Karten")
        
        for i in range(min(len(computer.hand), 10)):
            back = tk.Frame(self.computer_cards_frame, bg="#333333", 
                           width=50, height=80, relief=tk.RAISED, borderwidth=2)
            back.pack(side=tk.LEFT, padx=2)
        
        # Update discard pile history
        for widget in self.history_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.discard_pile_widget.winfo_children():
            widget.destroy()
        
        if self.game.discard_pile:
            # Show last 3-4 cards as history (scaled down and overlapped)
            history_count = min(3, len(self.game.discard_pile) - 1)
            if history_count > 0:
                history_cards = self.game.discard_pile[-(history_count+1):-1]
                for i, card in enumerate(history_cards):
                    card_frame = tk.Frame(self.history_cards_frame)
                    card_frame.pack(side=tk.LEFT, padx=(-30 if i > 0 else 0, 0))
                    
                    # Create smaller, semi-transparent looking cards
                    card_widget = CardWidget(card_frame, card, scale=0.6)
                    card_widget.configure(relief=tk.FLAT)
                    card_widget.pack()
                    
                    # Add transparency effect with overlay
                    overlay = tk.Frame(card_widget, bg="#006400", width=48, height=72)
                    overlay.place(x=0, y=0)
                    overlay.configure(bg="#006400", highlightthickness=0)
                    overlay.lower()
                    card_widget.configure(bg=card_widget.cget("bg"))
                    
                    # Make older cards appear more faded
                    opacity = 0.3 + (0.2 * i / history_count)
                    card_widget.winfo_children()[0].configure(
                        fg=card_widget.winfo_children()[0].cget("fg"))
            
            # Show current top card
            top_card = self.game.get_top_card()
            CardWidget(self.discard_pile_widget, top_card).pack()
        
        if self.game.declared_color:
            color_names = {
                Color.RED: "Rot",
                Color.BLUE: "Blau",
                Color.GREEN: "Grün",
                Color.YELLOW: "Gelb"
            }
            self.color_indicator.config(text=f"Aktuelle Farbe: {color_names[self.game.declared_color]}")
        else:
            self.color_indicator.config(text="")
        
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        
        self.player_card_frames = []
        player = self.game.players[0]
        
        # Update UNO button state
        if player.has_uno():
            self.uno_button.config(state=tk.NORMAL)
        else:
            self.uno_button.config(state=tk.DISABLED)
        
        for i, card in enumerate(player.hand):
            can_play = card.can_play_on(self.game.get_top_card(), self.game.declared_color)
            card_widget = CardWidget(self.player_cards_frame, card, 
                                   clickable=can_play and self.can_play,
                                   click_callback=lambda c, idx=i: self.play_card(idx))
            card_widget.pack(side=tk.LEFT, padx=5)
            self.player_card_frames.append(card_widget)
        
        current_player = self.game.players[self.game.current_player_index]
        self.status_label.config(text=f"{current_player.name} ist am Zug")
    
    def play_card(self, card_index):
        print(f"DEBUG: play_card called with index {card_index}")
        if not self.can_play:
            print(f"DEBUG: Cannot play - can_play is {self.can_play}")
            return
        
        player = self.game.players[0]
        if card_index >= len(player.hand):
            print(f"DEBUG: Invalid card index {card_index} (hand size: {len(player.hand)})")
            return
            
        card = player.hand[card_index]
        print(f"DEBUG: Attempting to play card: {card}")
        
        if not card.can_play_on(self.game.get_top_card(), self.game.declared_color):
            self.show_message("Diese Karte kannst du nicht spielen!")
            print(f"DEBUG: Card cannot be played on {self.game.get_top_card()}")
            return
        
        self.can_play = False
        
        played_card = player.play_card(card_index)
        self.game.discard_pile.append(played_card)
        self.game.declared_color = None
        
        self.show_message(f"Du spielst: {played_card}")
        
        if player.has_uno() and not player.has_called_uno:
            self.root.after(1000, self.check_uno_penalty)
        
        if card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            dialog = ColorSelectionDialog(self.root)
            self.root.wait_window(dialog)
            self.game.declared_color = dialog.selected_color
            self.show_message(f"Neue Farbe: {dialog.selected_color.value}")
        
        if card.card_type != CardType.NUMBER:
            self.handle_action_card(card)
        
        self.update_display()
        
        if len(player.hand) == 0:
            messagebox.showinfo("Gewonnen!", "Du hast gewonnen! 🎉")
            self.new_game()
            return
        
        self.game.current_player_index = (self.game.current_player_index + self.game.direction) % 2
        self.root.after(1500, self.computer_turn)
    
    def handle_action_card(self, card):
        next_player_index = (self.game.current_player_index + self.game.direction) % 2
        next_player = self.game.players[next_player_index]
        
        if card.card_type == CardType.SKIP:
            self.show_message(f"{next_player.name} setzt aus!")
            self.game.current_player_index = next_player_index
        
        elif card.card_type == CardType.REVERSE:
            self.game.direction *= -1
            self.show_message("Richtungswechsel!")
        
        elif card.card_type == CardType.DRAW_TWO:
            self.show_message(f"{next_player.name} muss 2 Karten ziehen!")
            for _ in range(2):
                next_player.draw_card(self.game.deck)
            self.game.current_player_index = next_player_index
        
        elif card.card_type == CardType.WILD_DRAW_FOUR:
            self.show_message(f"{next_player.name} muss 4 Karten ziehen!")
            for _ in range(4):
                next_player.draw_card(self.game.deck)
            self.game.current_player_index = next_player_index
    
    def computer_turn(self):
        computer = self.game.players[1]
        self.update_display()
        
        card_index = computer.choose_card(self.game.get_top_card(), self.game.declared_color)
        
        if card_index is None:
            self.show_message("Computer zieht eine Karte")
            drawn_card = computer.draw_card(self.game.deck)
            
            if drawn_card and drawn_card.can_play_on(self.game.get_top_card(), self.game.declared_color):
                self.show_message(f"Computer spielt gezogene Karte: {drawn_card}")
                self.game.discard_pile.append(drawn_card)
                self.game.declared_color = None
                
                if drawn_card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                    self.game.declared_color = computer.choose_color()
                    self.show_message(f"Computer wählt: {self.game.declared_color.value}")
                
                if drawn_card.card_type != CardType.NUMBER:
                    self.handle_action_card(drawn_card)
        else:
            card = computer.play_card(card_index)
            self.show_message(f"Computer spielt: {card}")
            self.game.discard_pile.append(card)
            self.game.declared_color = None
            
            if computer.has_uno() and random.random() > 0.1:
                computer.call_uno()
                self.show_message("Computer ruft UNO!")
            
            if card.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                self.game.declared_color = computer.choose_color()
                self.show_message(f"Computer wählt: {self.game.declared_color.value}")
            
            if card.card_type != CardType.NUMBER:
                self.handle_action_card(card)
        
        self.update_display()
        
        if len(computer.hand) == 0:
            messagebox.showinfo("Verloren!", "Der Computer hat gewonnen!")
            self.new_game()
            return
        
        self.game.current_player_index = (self.game.current_player_index + self.game.direction) % 2
        self.can_play = True
    
    def draw_card(self):
        if not self.can_play or self.game.current_player_index != 0:
            return
        
        player = self.game.players[0]
        drawn_card = player.draw_card(self.game.deck)
        
        if drawn_card:
            self.show_message(f"Gezogen: {drawn_card}")
            self.update_display()
            
            if drawn_card.can_play_on(self.game.get_top_card(), self.game.declared_color):
                response = messagebox.askyesno("Karte spielen?", 
                                             f"Möchtest du {drawn_card} spielen?")
                if response:
                    card_index = len(player.hand) - 1
                    self.play_card(card_index)
                    return
        
        self.can_play = False
        self.game.current_player_index = 1
        self.root.after(1500, self.computer_turn)
    
    def call_uno(self):
        player = self.game.players[0]
        if player.has_uno():
            player.call_uno()
            self.show_message("Du rufst UNO!")
    
    def check_uno_penalty(self):
        player = self.game.players[0]
        if player.has_uno() and not player.has_called_uno:
            self.show_message("UNO vergessen! 2 Strafkarten!")
            for _ in range(2):
                player.draw_card(self.game.deck)
            self.update_display()
    
    def show_message(self, message):
        # Cancel previous timer if exists
        if self.message_timer:
            self.root.after_cancel(self.message_timer)
        
        self.message_label.config(text=message)
        self.message_timer = self.root.after(3000, lambda: self.message_label.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app = UnoGUI(root)
    root.mainloop()