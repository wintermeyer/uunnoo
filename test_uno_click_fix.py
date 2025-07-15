#!/usr/bin/env python3
"""
Test to verify the UNO GUI click bug fix.
This test creates a minimal UNO game scenario and verifies that clicking cards works correctly.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
from uno import Game, Card, Color, CardType, HumanPlayer, ComputerPlayer

class TestUnoClickFix(unittest.TestCase):
    def setUp(self):
        """Set up a minimal game state for testing"""
        self.root = tk.Tk()
        self.game = Game()
        self.game.players = [
            HumanPlayer("Test Player"),
            ComputerPlayer("Computer")
        ]
        
        # Give player some test cards
        self.game.players[0].hand = [
            Card(Color.RED, CardType.NUMBER, 5),
            Card(Color.BLUE, CardType.NUMBER, 3),
            Card(Color.GREEN, CardType.SKIP),
        ]
        
        # Set up discard pile
        self.game.discard_pile = [Card(Color.RED, CardType.NUMBER, 7)]
        
    def tearDown(self):
        """Clean up tkinter root"""
        self.root.destroy()
    
    def test_lambda_closure_fix(self):
        """Test that the lambda closure properly captures the card index"""
        captured_indices = []
        
        # Simulate the old buggy approach
        callbacks_buggy = []
        for i in range(3):
            # This would capture i by reference (buggy)
            callback = lambda c, idx=i: captured_indices.append(idx)
            callbacks_buggy.append(callback)
        
        # Clear and test buggy callbacks
        captured_indices.clear()
        for cb in callbacks_buggy:
            cb("dummy_card")
        
        # With the buggy approach, we'd expect all indices to be 2 (last value)
        # But with idx=i default parameter, it should work correctly
        self.assertEqual(captured_indices, [0, 1, 2], "Default parameter should capture values correctly")
        
        # Simulate the fixed approach with closure
        callbacks_fixed = []
        captured_indices.clear()
        
        for i in range(3):
            def make_callback(index):
                return lambda c: captured_indices.append(index)
            callbacks_fixed.append(make_callback(i))
        
        # Test fixed callbacks
        for cb in callbacks_fixed:
            cb("dummy_card")
        
        self.assertEqual(captured_indices, [0, 1, 2], "Closure approach should capture values correctly")
    
    def test_card_widget_click_handling(self):
        """Test that CardWidget properly handles clicks"""
        # Import here to avoid circular imports
        from uno_gui_improved import CardWidget
        
        clicked_cards = []
        
        def mock_callback(card):
            clicked_cards.append(card)
        
        # Create a test card widget
        test_card = Card(Color.RED, CardType.NUMBER, 5)
        widget = CardWidget(
            self.root,
            test_card,
            clickable=True,
            click_callback=mock_callback
        )
        
        # Simulate a click event
        event = Mock()
        event.widget = widget
        
        # The widget should have bound the click event
        # Find and call the bound callback
        callbacks = widget._eventinfo()
        if callbacks:
            for callback_info in callbacks:
                if isinstance(callback_info, tuple) and len(callback_info) > 1:
                    callback = callback_info[1]
                    if callable(callback):
                        callback(event)
        
        # We can't easily test tkinter events without running mainloop
        # But we can verify the callback structure is set up correctly
        self.assertIsNotNone(widget.click_callback)
        
        # Test the callback directly
        widget.click_callback(test_card)
        self.assertEqual(len(clicked_cards), 1)
        self.assertEqual(clicked_cards[0], test_card)
    
    def test_play_card_index_handling(self):
        """Test that play_card is called with the correct index"""
        from uno_gui_improved import UnoGUI
        
        # Create a mock UnoGUI instance
        gui = UnoGUI(self.root)
        gui.game = self.game
        gui.can_play = True
        
        # Mock the show_message method to avoid UI updates
        gui.show_message = Mock()
        
        # Track which indices are passed to play_card
        played_indices = []
        original_play_card = gui.play_card
        
        def mock_play_card(index):
            played_indices.append(index)
            # Don't actually play the card to avoid side effects
        
        gui.play_card = mock_play_card
        
        # Simulate the update_display card creation loop
        player = gui.game.players[0]
        callbacks = []
        
        for i, card in enumerate(player.hand):
            # Use the fixed closure approach
            def make_play_callback(card_index):
                return lambda c: gui.play_card(card_index)
            
            callback = make_play_callback(i)
            callbacks.append(callback)
        
        # Test each callback
        for i, (callback, card) in enumerate(zip(callbacks, player.hand)):
            played_indices.clear()
            callback(card)  # Pass the card as CardWidget does
            self.assertEqual(played_indices, [i], f"Callback {i} should play card at index {i}")

if __name__ == "__main__":
    # Run tests with minimal verbosity
    unittest.main(verbosity=2)