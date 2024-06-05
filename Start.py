"""
author: Ofri Guz
Date: 01/06/24
description: start class that prepares decks for game
"""
import random


class START:
    def __init__(self, num_of_players):

        self.num_of_players = num_of_players
        self.decks = []
        self.removed_cards = []

    def create_cards(self):
        """
        Create deck of cards and split according to number of players
        creates a full deck of cards, shuffles it, and then splits it into individual decks for each player.
        The decks are stored in the 'decks' attribute

        :return: A list of each player's deck.
        :rtype: list of tuples
        """
        full_deck = list(range(1, 3)) * 4 + list(range(3, 10)) * 6 + list(range(0, 1)) * 6 + list(range(10, 12)) * 8
        random.shuffle(full_deck)
        tuple_length = len(full_deck) // self.num_of_players
        # split into personal decks
        for i in range(self.num_of_players):
            start_index = i * tuple_length
            end_index = (i + 1) * tuple_length
            split_deck = tuple(full_deck[start_index:end_index])
            self.decks.append(split_deck)
        # PRINT DECKS
        #  for i, deck in enumerate(self.decks, start=1):
        #    print(f"deck_{i}:", deck)
        return self.decks
