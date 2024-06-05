"""
author: Ofri Guz
Date: 01/06/24
description: game class that handles the game rules
"""
#  constants
GHOST = 10
HALF = 11
ZERO = 0


class GAME:
    def __init__(self, discard_pile, card_played, removed_cards):
        """
        Initialize GAME class
        :param discard_pile: Array of all cards in the discard pile
        :type discard_pile: list
        :param card_played: card wanting to be played
        :type card_played: int
        :param removed_cards: List of cards in players hand
        :type removed_cards: list
        """
        self.discard_pile = discard_pile  # array of all cards in the discard pile
        self.card_played = card_played  # the card wanting to be played
        self.last_card_played = discard_pile[-1] if discard_pile else None
        self.second_last_card = discard_pile[-2] if len(discard_pile) > 1 else None
        self.removed_cards = removed_cards

    def set_removed_cards(self, removed_cards):
        """
        set removed cards (cards in hand)
        :param removed_cards:  list of cards in hand
        :return:
        """
        self.removed_cards = removed_cards

    def set_discard_pile(self, discard_pile):
        """
        set discard pile
        :param discard_pile: Array of all cards in the discard pile
        :return:
        """
        self.discard_pile = discard_pile

    def set_card_played(self, card_played):
        """
        set card played
        :param card_played: The card wanting to be played
        :return:
        """
        self.card_played = card_played

    def empty_discard_pile(self):
        """
        check that the card played is not special
        :return:True if the card played is not special, False otherwise
        :rtype: bool
        """
        if self.card_played == GHOST or self.card_played == HALF or self.card_played == ZERO:
            return False
        else:
            return True  # If the discard pile is empty, any card (that's not special) can be played

    def last_card_ghost(self):
        """
        Find the last card played that isn't a ghost
        :return:
        """
        i = 2
        while self.last_card_played == GHOST:
            self.last_card_played = self.discard_pile[0 - i]
            i = i + 1

    def last_card_half(self):
        """
        Find the value the discard pile is at now (if the last card played was a HALF)
        :return:
        """
        i = 3
        count = 1
        while self.second_last_card == GHOST or self.second_last_card == HALF:
            if self.second_last_card == HALF:
                count = count + 1
            self.second_last_card = self.discard_pile[0 - i]
            i = i + 1
        add = count / 2
        self.last_card_played = self.second_last_card + add

    def last_card_five(self):
        """
        if the last card played was a 5:
        check if current card played is less than or equal to 5 or a special card
        :return: True if the card played is less than or equal to 5 or a special card, False otherwise.
        :rtype: bool
        """
        if self.card_played <= 5 or self.card_played >= 10:
            return True
        else:
            return False

    def is_card_valid(self):
        """
        Check if the card played is valid according to the game rules
        :return: True if card played is valid, False otherwise
        :rtype: bool
        """
        if not self.discard_pile:  # Check if the discard pile is empty
            return self.empty_discard_pile()
        if self.last_card_played == GHOST:
            self.last_card_ghost()
        if self.last_card_played == HALF:
            self.last_card_half()
        if self.last_card_played == 5:
            return self.last_card_five()
        if self.card_played == ZERO:
            if not float(self.last_card_played).is_integer():  # Check if last card played is whole number
                return False
            return True
        if self.last_card_played == 8.5:
            if self.card_played == 9 or self.card_played == GHOST:
                return True
            else:
                return False
        if self.card_played == GHOST or self.card_played == HALF:
            return True
        if 0 <= self.last_card_played <= 9:
            if self.card_played >= self.last_card_played:
                return True
            else:
                return False

    def have_valid_card(self):
        """
        Checks if player has a valid card that can be played
        :return: True if player has a valid card, otherwise False
        :rtype: bool
        """
        for i in range(len(self.removed_cards)):
            self.card_played = self.removed_cards[i]
            if self.is_card_valid():
                return True
        return False


def test_game_class():
    try:
        # Test scenario 1: Empty discard pile and a non-special card
        game1 = GAME([], 7, [3, 4, 5])
        assert game1.is_card_valid() is True, "Test scenario 1 failed"

        # Test scenario 2: Empty discard pile and a special card (GHOST)
        game2 = GAME([], GHOST, [3, 4, 5])
        assert game2.is_card_valid() is False, "Test scenario 2 failed"

        # Test scenario 3: Last card in discard pile is GHOST
        game3 = GAME([1, 3, GHOST, 5, 3, GHOST, GHOST], 9, [3, 4, 5])
        game3.last_card_ghost()
        assert game3.last_card_played == 3, "Test scenario 3 failed"

        # Test scenario 4: Last card in discard pile is HALF
        game4 = GAME([2, 3, GHOST, HALF], 9, [3, 4, 5])
        game4.last_card_half()
        assert game4.last_card_played == 3.5, "Test scenario 4 failed"

        # Test scenario 5: Last card in discard pile is 5 and card played is less than or equal to 5
        game5 = GAME([1, 2, 5], 3, [3, 4, 5])
        assert game5.is_card_valid() is True, "Test scenario 5 failed"

        # Test scenario 6: Last card in discard pile is 5 and card played is greater than 5 but less than 10
        game6 = GAME([2, 5, 5], 6, [3, 4, 5])
        assert game6.is_card_valid() is False, "Test scenario 6 failed"

        # Test scenario 7: Last card in discard pile is 5 and card played is special
        game7 = GAME([1, 2, 3, 5], 10, [3, 4, 5])
        assert game7.is_card_valid() is True, "Test scenario 7 failed"

        # Test scenario 8: Last card in discard pile is an even number and card played is ZERO
        game8 = GAME([1, 2, 3, 6, GHOST], ZERO, [3, 4, 5])
        assert game8.is_card_valid() is True, "Test scenario 8 failed"

        # Test scenario 9: Last card in discard pile is an odd number and card played is ZERO
        game9 = GAME([2, 7, GHOST], ZERO, [3, 4, 5])
        assert game9.is_card_valid() is True, "Test scenario 9 failed"

        # Test scenario 10: Last card in discard pile is 8.5 and card played is 9
        game10 = GAME([3, HALF, 8, HALF], 9, [3, 4, 5])
        assert game10.is_card_valid() is True, "Test scenario 10 failed"

        # Test scenario 11: Last card in discard pile is 8.5 and card played is not 9
        game11 = GAME([8, HALF], HALF, [3, 4, 5])
        assert game11.is_card_valid() is False, "Test scenario 11 failed"

        # Test scenario 12: Last card in discard pile is a regular number and card played is higher
        game12 = GAME([5, HALF, HALF, GHOST, HALF, HALF, GHOST, GHOST], 8, [3, 4, 5])
        assert game12.is_card_valid() is True, "Test scenario 12 failed"

        # Test scenario 13: Last card in discard pile is a regular number and card played is lower
        game13 = GAME([7], 6, [3, 4, 5])
        assert game13.is_card_valid() is False, "Test scenario 13 failed"

        # Test scenario 14: Valid card in removed cards
        game14 = GAME([5], 3, [4, 6, 5])
        assert game14.have_valid_card() is True, "Test scenario 14 failed"

        # Test scenario 15: No valid card in removed cards
        game15 = GAME([5], 3, [1, 2, 4])
        assert game15.have_valid_card() is True, "Test scenario 15 failed"

        game16 = GAME([7, HALF], ZERO, [1, 2, 4])
        assert game16.is_card_valid() is False, "Test scenario 16 failed"

        game17 = GAME([8, HALF], GHOST, [1, 2, 4])
        assert game17.is_card_valid() is True, "Test scenario 17 failed"

        game18 = GAME([5, HALF, HALF], 6, [1, 2, 4])
        assert game18.is_card_valid() is True, "Test scenario 18 failed"

        print("All tests passed!")
    except AssertionError as e:
        print(e)


def main():
    """
    Add Documentation here
    """
    test_game_class()


if __name__ == '__main__':
    main()
