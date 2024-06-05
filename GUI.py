import pygame
import sys

import Welcome

#  constants
GHOST = 10
HALF = 11
ZERO = 0
CARD_WIDTH = 120
CARD_HEIGHT = 150
REFRESH_RATE = 60
CLOCK = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = "Comic Sans MS"
BACKGROUND = "background.jpg"
CARD_ZERO = "card_0.jpg"
CARD_ONE = "card_1.jpg"
CARD_TWO = "card_2.jpg"
CARD_THREE = "card_3.jpg"
CARD_FOUR = "card_4.jpg"
CARD_FIVE = "card_5.jpg"
CARD_SIX = "card_6.jpg"
CARD_SEVEN = "card_7.jpg"
CARD_EIGHT = "card_8.jpg"
CARD_NINE = "card_9.jpg"
CARD_TEN = "card_10.jpg"
CARD_ELEVEN = "card_11.jpg"
DISCARD_PILE_PLACE_ROW = 390
DISCARD_PILE_PLACE_COLUMN = 200
CARD_PLACE_ROW = 400
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600


class GUI:
    """
    Manages the gui using pygame
    """
    def __init__(self, decks, player_num, removed_cards, discard_pile, card_pressed):
        """
        Initialize the GUI
        :param decks: List of decks
        :param player_num: Player Number
        :param removed_cards: List of cards in hand
        :param discard_pile: List of cards in the discard pile
        :param card_pressed: Card pressed by the player
        """
        self.card_pressed = card_pressed
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player_num = player_num
        pygame.display.set_caption("8 1/2")
        self.removed_cards = removed_cards
        self.buttons = [
            pygame.Rect(250, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(DISCARD_PILE_PLACE_ROW, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(530, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT)]
        self.two = [
            pygame.Rect(320, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(460, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT)]
        self.decks = decks
        self.discard_pile = discard_pile
        self.card_value = None
        self.bank = [None] * len(self.removed_cards)

    def open_welcome_page(self):
        welcome_page = Welcome.WelcomePage(self.player_num)
        welcome_page.display()  # Assuming this method displays the welcome page and handles the button press
        return welcome_page.start_game  # Modify the WelcomePage class to have a start_game attribute

    def set_player_num(self, player_num):
        """
        Set the player number
        :param player_num: Player number
        :return:
        """
        self.player_num = player_num

    def set_deck(self, decks):
        """
        Set deck of cards
        :param decks: List of cards in the deck
        :return:
        """
        self.decks = decks

    def get_deck(self):
        """
        Get deck of cards
        :return: List of cards in deck
        """
        return self.decks

    def set_removed_cards(self, removed_cards):
        """
        Set the removed cards (cards in hand)
        :param removed_cards: List of the cards in players hand
        :return:
        """
        self.removed_cards = removed_cards

    def get_removed_cards(self):
        """
        Get the removed cards (cards in hand)
        :return: List of cards in players hand
        """
        return self.removed_cards

    def get_player_num(self):
        """
        Get player number
        :return: Player number
        """
        return self.player_num

    def set_card_pressed(self, card_pressed):
        """
        Set the card pressed by the player
        :param card_pressed: Card pressed by the player
        :return:
        """
        self.card_pressed = card_pressed

    def set_discard_pile(self, discard_pile):
        """
        Set the discard pile
        :param discard_pile: List of cards in the discard pile
        :return:
        """
        self.discard_pile = discard_pile

    def get_card_pressed(self):
        """
        Get the card pressed by the player
        :return: Card pressed by the player
        """
        return self.card_pressed

    def create_screen(self):
        """
        create screen and display the last card pressed (if any)
        """
        img = pygame.image.load(BACKGROUND)
        # fill screen and show
        self.screen.blit(img, (0, 0))
        # draw left card
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(250, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT))
        # draw middle card
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(DISCARD_PILE_PLACE_ROW, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT))
        # draw right card
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(530, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT))
        # draw chabila
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(30, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT))
        # draw discard pile
        pygame.draw.rect(surface=self.screen, color=WHITE, rect=pygame.Rect(DISCARD_PILE_PLACE_ROW,
                                                                            DISCARD_PILE_PLACE_COLUMN,
                                                                            CARD_WIDTH, CARD_HEIGHT))
        if self.discard_pile:  # Check if the discard pile is not empty
            # Draw the discard pile only if it's not empty
            card_value = self.discard_pile[-1]
            card_image = pygame.image.load(f"card_{card_value}.jpg")
            card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            self.screen.blit(card_image, (DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN))
        pygame.display.flip()
        pygame.font.init()

    def print_cards(self, game_state):
        """
        Print the cards in hand
        :param game_state: The state of the game (whether to print 3, 2, 1 cards)
        """
        for i, removed in enumerate(self.removed_cards):
            print(f"Cards in hand_{self.player_num}:", removed)
            card_image = pygame.image.load(f"card_{removed}.jpg")
            card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            if game_state == "TWO":
                self.screen.blit(card_image, self.two[i].topleft)
            elif game_state == "ONE":
                self.screen.blit(card_image, self.buttons[1].topleft)
            else:
                self.screen.blit(card_image, self.buttons[i].topleft)
        pygame.display.flip()
        self.draw_num_of_cards_left()

    def draw_player_number(self, player_num):
        """
        Draw the player number on the screen
        :param player_num: Player number
        """
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"Your player num: {player_num}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 50))
        self.screen.blit(text_surface, (20, 20))
        # pygame.display.set_caption("8 1/2 Player:")
        pygame.display.flip()

    def draw_num_of_cards_left(self):
        """
        Draw the number of cards left in deck
        """
        font = pygame.font.Font(None, 40)
        text_surface = font.render(str(len(self.decks)), True, BLACK)
        chabila_rect = pygame.Rect(30, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT)
        text_rect = text_surface.get_rect(center=chabila_rect.center)
        self.screen.fill(WHITE, chabila_rect)
        # Draw the text
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def draw_current_player(self, current_player):
        """
        Draw the current player on the screen
        :param current_player: Current player number
        """
        font = pygame.font.Font(None, 30)
        text_surface = font.render(f"Current player: {current_player}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 70, 200, 50))
        self.screen.blit(text_surface, (20, 80))
        pygame.display.flip()

    def print_card(self):
        """
        Draw the cards in hand on the screen
        """
        for i, removed in enumerate(self.removed_cards):
            print(f"Cards in hand_{self.player_num}:", removed)
            card_image = pygame.image.load(f"card_{removed}.jpg")
            card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            self.screen.blit(card_image, self.buttons[i].topleft)
        pygame.display.flip()

    def choose_card(self):
        """
        wait for player to choose (click on) a card
        :return: card_pressed - the card the player chose
        """
        while True:
            for play in pygame.event.get():
                if play.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif play.type == pygame.MOUSEBUTTONDOWN and play.button == 1:
                    place = pygame.mouse.get_pos()
                    for i, button_rect in enumerate(self.buttons, start=1):
                        if button_rect.collidepoint(place):
                            print(f"Card {i}")
                            self.card_pressed = i
                            # self.card_value = self.removed_cards[self.player_num - 1][self.card_pressed - 1]%
                            self.card_value = self.removed_cards[self.card_pressed - 1]

                            return self.card_pressed
            pygame.display.flip()
            CLOCK.tick(REFRESH_RATE)

    def move_to_middle(self, removed_cards, card_pressed):
        """
        Move the chosen card to the middle (discard_pile)
        :param removed_cards: List of removed cards
        :param card_pressed: Card pressed by the player
        """
        # self.card_value = removed_cards[player_num - 1][card_pressed - 1] %
        self.card_value = removed_cards[card_pressed - 1]

        self.discard_pile.append(self.card_value)
        card_image = pygame.image.load(f"card_{self.card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        self.screen.blit(card_image, (DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN))
        pygame.display.flip()

    def draw_new_card(self, card_pressed):
        """
        Draw a new card in the player's hand
        :param card_pressed: Card pressed by the player
        """
        button_rect = self.buttons[card_pressed - 1]  # Get the rectangle corresponding to the card_pressed
        # card_value = self.removed_cards[self.player_num - 1][-1] %
        card_value = self.removed_cards[-1]

        card_image = pygame.image.load(f"card_{card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        self.screen.blit(card_image, button_rect)
        pygame.display.flip()

        # Update the order of cards in removed_cards for the current player
        beg = self.removed_cards[:card_pressed - 1]
        end = self.removed_cards[card_pressed - 1:-1]
        self.removed_cards = beg + [card_value] + end
        print(self.removed_cards)

    def draw_middle(self, card_value):
        """
        draw middle card (most recent card played)
        :param card_value: Value of card to be drawn
        """
        # Load the card image based on the card_value parameter
        card_image = pygame.image.load(f"card_{card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))

        # Draw the card image in the middle square
        middle_rect = pygame.Rect(DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN, CARD_WIDTH, CARD_HEIGHT)
        self.screen.blit(card_image, middle_rect.topleft)

        # Update the display
        pygame.display.flip()
        self.draw_num_of_cards_left()

    def replace_chosen_card(self, card_pressed, removed_cards):
        """
        Replace chosen card with another card from the deck
        :param card_pressed: card chosen
        :param removed_cards: cards in hand
        :return: removed cards if any, otherwise, False
        """
        if self.decks:
            # Remove the card at the chosen position from the player's hand
            removed_cards = removed_cards[:card_pressed - 1] + removed_cards[card_pressed:]

            removed_cards.append(self.decks[0])

            # Remove the added card from the player's deck
            self.decks = self.decks[1:]
            return removed_cards
        else:
            return False

    def display_message(self, text):
        """
        Display message on screen
        :param text: text to be displayed
        :return:
        """
        # Render the message with a white highlight
        text_font_highlight = pygame.font.SysFont(FONT, 40)
        text_surface_highlight = text_font_highlight.render(text, True, WHITE)
        text_rect_highlight = text_surface_highlight.get_rect(center=(450, 300))

        # Render the actual text in black color
        text_font = pygame.font.SysFont(FONT, 40)
        text_surface = text_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(450, 300))

        # Display the message with the white highlight and black text
        self.screen.blit(text_surface_highlight, text_rect_highlight)
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  # Wait for 1000 milliseconds (1 second)

    def restart(self):
        """
        redraw screen how it was (the screen, cards in players hand, most recent card in the discard pile)
        :return:
        """
        # draw discard pile
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN, CARD_WIDTH, CARD_HEIGHT))
        pygame.display.flip()
        pygame.font.init()
        self.bank[self.player_num - 1] = self.discard_pile
        self.discard_pile.clear()
        self.create_screen()  # Re-create the screen to update the display
        self.print_cards("")  # Print the cards for the current player
        pygame.display.flip()

    def redo(self):
        """
        draw an empty discard pile
        """
        # draw discard pile
        pygame.draw.rect(surface=self.screen, color=WHITE,
                         rect=pygame.Rect(DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN, CARD_WIDTH, CARD_HEIGHT))
        pygame.display.flip()

    def draw_last_cards(self):
        """
        draw last card in players hand
        :return:
        """
        self.create_screen()
        beg = self.removed_cards[:self.card_pressed-1]
        end = self.removed_cards[self.card_pressed:]
        self.removed_cards = beg + end
        self.card_value = self.removed_cards[0]
        card_image = pygame.image.load(f"card_{self.card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        self.screen.blit(card_image, (DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN))

        card_image = pygame.image.load(f"card_{self.card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        self.screen.blit(card_image, self.buttons[1].topleft)
        pygame.display.flip()
        print(self.removed_cards)

    def draw_two_cards(self):
        """
        draw last two cards in players hand
        """
        # clear screen
        self.create_screen()
        self.card_value = self.removed_cards[self.card_pressed - 1]
        card_image = pygame.image.load(f"card_{self.card_value}.jpg")
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        self.screen.blit(card_image, (DISCARD_PILE_PLACE_ROW, DISCARD_PILE_PLACE_COLUMN))
        beg = self.removed_cards[:self.card_pressed-1]
        end = self.removed_cards[self.card_pressed:]
        self.removed_cards = beg + end
        for i, removed in enumerate(self.removed_cards):
            print(f"Cards in hand_{self.player_num}:", removed)
            card_image = pygame.image.load(f"card_{removed}.jpg")
            card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
            self.screen.blit(card_image, self.two[i].topleft)
        pygame.display.flip()
        print(self.removed_cards)


def check_assertions():
    # Assertions

    # Check if player number can be set and retrieved correctly
    gui = GUI([], 1, [], [], None)
    gui.set_player_num(2)
    assert gui.get_player_num() == 2

    # Check if deck setting and retrieval work correctly
    decks = [1, 2, 3, 4, 5]
    gui.set_deck(decks)
    assert gui.get_deck() == decks

    # Check if removed cards can be set and retrieved correctly
    removed_cards = [6, 7, 8, 9, 10]
    gui.set_removed_cards(removed_cards)
    assert gui.get_removed_cards() == removed_cards

    # Check if card pressed can be set and retrieved correctly
    gui.set_card_pressed(3)
    assert gui.get_card_pressed() == 3

    # Check if discard pile can be set and retrieved correctly
    discard_pile = [11, 12, 13]
    gui.set_discard_pile(discard_pile)
    assert gui.discard_pile == discard_pile


if __name__ == '__main__':
    check_assertions()
