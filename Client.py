"""
author: Ofri Guz
Date: 01/06/24
description: client which connects to server
"""
import socket
import threading
import time
import traceback
import pygame
import Game
import GUI
import Protocol
import logging
import Welcome

#  constants
MAX_PACKET = 1024  # Maximum size of packet to be received
IP = '127.0.0.1'  # Server IP address
PORT = 8820  # Server port number
SEPERATOR = '$'  # Separator used in messages
CARD_WIDTH = 120  # Width of a card
CARD_HEIGHT = 150  # Height of a card
CARD_PLACE_ROW = 400  # Row position where cards are placed
BUTTONS = [
            pygame.Rect(250, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(390, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(530, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT)]

TWO_BUTTONS = [
            pygame.Rect(320, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT),
            pygame.Rect(460, CARD_PLACE_ROW, CARD_WIDTH, CARD_HEIGHT)]

# global variables
runs = True  # Flag to control the main loop
gui: GUI.GUI  # GUI instance
discard_pile = []  # List to store cards in the discard pile
saved_discard = []  # List to store saved discarded cards
game: Game.GAME  # Game instance
your_turn = False  # Flag to indicate if it's the player's turn
waiting_to_send = []  # List of messages waiting to be sent to the server
client_socket: socket.socket  # Client socket
current_deck = []  # List to store the current deck
game_state = None  # Variable to store the current state of the game
welcome_page: Welcome.WelcomePage


def receive_deck(message_str):
    """
        Receives the deck from the server message
        :param message_str: String message from the server
        :return: List of integers representing the deck
    """
    try:
        # Check if the message is empty
        if not message_str:
            raise ValueError("Received empty message from server")

        # Check if the message starts with '$'
        if not message_str.startswith('DEK$'):
            raise ValueError("Invalid message format: Message does not start with 'DECKS$'")
        # Remove the leading '$' character
        message_str = message_str[4:]
        # Convert the string back into a list of integers
        if message_str:
            message_list = list(map(int, message_str.split(SEPERATOR)))
        else:
            message_list = []
        return message_list
    except Exception as e:
        logging.error("Error receiving deck: %s", e)
        raise


def hand_out_cards(deck):
    """
       Hand out first 3 cards to player
       :param deck: List of integers representing the personal deck (player's cards)
       :return: Tuple containing the updated deck and the cards in the player's hand
    """
    if len(deck) >= 3:
        # Remove first 3 cards and store them in a list
        removed = deck[:3]
        # Update the deck (remove the first 3 cards)
        deck = deck[3:]
    else:
        print("Not enough cards in the deck")
        removed = []
    return removed, deck


def send_message(my_socket, msg_type, current_card, did_win, player, did_turn):
    """
    sends message to server
    :param my_socket: Socket to send the message through
    :param msg_type: message type
    :param current_card: Card played
    :param did_win: Whether the player won the game
    :param player: Number Player
    :param did_turn: Whether the player did a move
    :return:
    """
    try:
        message = f"{msg_type}${current_card}${did_win}${player}${did_turn}"
        msg = Protocol.protocol_client_send(message)
        logging.info('Sending message: %s', msg)
        my_socket.send(msg.encode())
    except Exception as e:
        logging.error("Error sending message: %s", e)


def add_to_waiting_list(msg_type, current_card, did_win, player, did_turn):
    """
    Add message to waiting to send list
    :param msg_type: message type
    :param current_card: Card played
    :param did_win: Whether the player won the game
    :param player: Number Player
    :param did_turn: Whether the player did a move
    """
    global waiting_to_send
    message = f"{msg_type}${current_card}${did_win}${player}${did_turn}"
    logging.info('waiting to send %s', message)
    waiting_to_send.append(message)


def lowest_card(cards_in_hand):
    """
    Finds lowest yellow card in player's hand
    :param cards_in_hand: cards in player's hand
    :return: the lowest yellow card in player's hand or 15 if no yellow cards are found
    """
    lowest_card_value = 15
    for card in cards_in_hand:
        if (1 <= card <= 4 or 6 <= card <= 9) and card < lowest_card_value:
            lowest_card_value = card
    return lowest_card_value  # if equal to 15 means no yellow cards


def receive_update(message_str):
    """
    Receive update message
    :param message_str: message from server
    :return: components of update message -
    :return: new_card_placed: new card played did_win_bool: whether the game ended, player: current player
    """
    # Check if the message is empty
    if not message_str:
        raise ValueError("Received empty message from server")

    logging.info('received message %s', message_str)

    # Check if the message starts with '$'
    if not message_str.startswith('UPD$'):
        raise ValueError("Invalid message format: Message does not start with 'DON$'")

    # Remove the leading '$' character
    message_str = message_str[4:]

    # Convert the string back into a list of integers
    did_win, player, new_card_placed, = message_str.split(SEPERATOR)
    did_win_bool = True
    if did_win == "False":
        did_win_bool = False
    return new_card_placed, did_win_bool, int(player)


def handle_client_messages():
    """
    Handles messages that need to be sent to the server
    """
    global client_socket
    global waiting_to_send
    while True:
        try:
            if waiting_to_send is not None and len(waiting_to_send) > 0:
                for message_to_send in waiting_to_send:
                    try:
                        message = Protocol.protocol_client_send(message_to_send)
                        logging.info('message sending to server: %s', message)
                        print("Message sending to server:", message)
                        client_socket.send(message.encode())
                        waiting_to_send.remove(message_to_send)
                    except Exception as e:
                        logging.error("Error in sending message loop: %s", e)
                        time.sleep(5)
        except Exception as e:
            stack_trace = traceback.format_exc()
            print(stack_trace)
            print(f"Error handling client messages: {e}")
            time.sleep(5)  # Sleep for 5 seconds


def handle_server_connection():
    """
    Handles the connection to the server and processes incoming messages
    """
    global runs
    global gui
    global discard_pile
    global saved_discard
    global game
    global your_turn
    global client_socket

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            client_socket.connect((IP, PORT))
            print("Connected to server")
            logging.info('Connected to server')
            break
        except Exception as e:
            print(f"Error connecting to server: {e}")
            time.sleep(5)  # Sleep for 2 seconds
    while runs:
        try:
            print("waiting to receive message from the server")
            logging.info("waiting to receive message from the server")
            data = Protocol.protocol_receive(client_socket)
            print("Received from server:", data)
            logging.info("Received from server: %s", data)
            if data.startswith('NUM$'):
                handle_num_message(data)

            elif data.startswith('DEK$'):
                deck = receive_deck(data)
                cards_in_hand, deck = hand_out_cards(deck)
                send_message(client_socket, 'LOW', lowest_card(cards_in_hand), False, gui.get_player_num(), True)
                print("Cards in hand:", cards_in_hand)
                print("Remaining deck:", deck)
                if gui is None:
                    print("GUI IS NONE")
                    logging.info("GUI IS NONE")
                else:
                    gui.set_deck(deck)
                    print(gui.get_deck())
                    gui.set_removed_cards(cards_in_hand)
                    gui.print_cards(game_state)
            elif data.startswith("UPD$"):
                handle_update_message(data)
            else:
                print("Unexpected message")
                logging.warning("Unexpected message")
        except ConnectionResetError as e:
            logging.error(f"Connection was reset: %s",e)
            raise
        except Exception as e:
            stack_trace = traceback.format_exc()
            print(stack_trace)
            logging.error("Error receiving data from server: %s", e)


def handle_num_message(data):
    """
    Handles the NUM message from the server, setting the player number
    :param data: String message from the server
    """
    global gui, welcome_page
    player_num = data[4:]
    if gui is None:
        print("GUI IS NONE")
        logging.info("GUI IS NONE")
    else:
        player_num = int(player_num)
        gui.set_player_num(player_num)
        gui.draw_player_number(player_num)


def handle_update_message(data):
    """
    Handles the UPDATE message from the server
    :param data: String message from the server
    """
    global discard_pile, game, your_turn, saved_discard, gui, client_socket
    new_card_placed, did_win, player = receive_update(data)
    print("Current player: " + str(player) + " New card placed: " + new_card_placed)
    gui.draw_current_player(player)
    player = int(player)
    if new_card_placed == "EMPTY":
        gui.redo()
        discard_pile = []
    else:
        new_card_placed = int(new_card_placed)
        gui.draw_middle(new_card_placed)
        discard_pile.append(new_card_placed)  # double check not adding twice
    print("Discard pile:", discard_pile, "Current Player:", player, "Player Num:", gui.get_player_num())
    if int(player) == gui.get_player_num() and did_win is False:
        game = Game.GAME(discard_pile, 0, gui.get_removed_cards())
        print("Are cards valid?", game.have_valid_card())
        if not game.have_valid_card():
            your_turn = False
            gui.display_message("No Valid Card")
            if discard_pile:
                saved_discard += discard_pile
            last_card = "EMPTY"
            gui.create_screen()
            gui.print_cards(game_state)
            gui.draw_player_number(gui.get_player_num())
            send_message(client_socket, "DON", last_card, False, gui.get_player_num(), False)
        else:
            your_turn = True
    else:
        your_turn = False
    if did_win is True:
        print("Player " + str(player) + " won!!")
        logging.info("Player " + str(player) + " won!!")
        gui.display_message("Player " + str(player) + " won!!")


def start_connection():
    """
    Starts the connection to the server and initializes threads for handling server connection and client messages
    """
    connection_thread = threading.Thread(target=handle_server_connection)
    connection_thread.daemon = True  # This makes the thread exit when the main program exits
    connection_thread.start()
    connection_thread_client_messages = threading.Thread(target=handle_client_messages)
    connection_thread_client_messages.daemon = True  # This makes the thread exit when the main program exits
    connection_thread_client_messages.start()


def main():
    """
    Sends messages to server and get responses
    """

    global gui, welcome_page
    global your_turn
    global game
    try:
        open_gui("", "", 1)
        if gui is None:
            print("GUI IS NONE")
            logging.info("GUI IS NONE")

    # ip = input("What ip address would you like to connect to? ")
    # start_connection(ip)

        welcome_page = Welcome.WelcomePage(gui.get_player_num())
        welcome_page.display()
        while not welcome_page.get_start_game():
            welcome_page.run_welcome_page()
        welcome_page.restart_screen()
        gui.create_screen()
        start_connection()
        running = True
        while running:
            try:
                for event in pygame.event.get():
                    # print("Your Turn: " + str(your_turn))
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and your_turn:
                        place = pygame.mouse.get_pos()
                        print("Game State: " + str(game_state))
                        if game_state == "TWO":
                            for i, button_rect in enumerate(TWO_BUTTONS, start=1):
                                if button_rect.collidepoint(place):
                                    press_on_card(i)
                        elif game_state == "ONE":
                            if BUTTONS[1].collidepoint(place):
                                press_on_card(1)
                        else:
                            for i, button_rect in enumerate(BUTTONS, start=1):
                                if button_rect.collidepoint(place):
                                    press_on_card(i)
            except Exception as e:
                logging.error(f"Error in main event loop: {e}")
    except Exception as e:
        logging.error(f"Error in main function: {e}")
    finally:
        pygame.quit()
        stop_connection()


def press_on_card(card_position):
    """
    Handles the event when a card is pressed by the player
    :param card_position: Position of the card pressed
    """
    global gui
    global game, your_turn, current_deck, game_state

    try:
        print(f"Pressed Card position :  {card_position}")
        print("cards in hand:", gui.get_removed_cards())
        gui.set_card_pressed(card_position)
        card_value = gui.get_removed_cards()[gui.get_card_pressed() - 1]
        print(f"card value:  {card_value}")
        game = Game.GAME(discard_pile, card_value, gui.get_removed_cards())
        print("Is card valid?", game.is_card_valid())

        if game.is_card_valid():
            gui.move_to_middle(gui.get_removed_cards(), gui.get_card_pressed())
            # next_card = gui.replace_chosen_card(gui.get_card_pressed(), gui.get_removed_cards())
            current_deck = gui.get_deck()
            print("current deck: " + str(current_deck))

            # gui.set_removed_cards(next_card)
            print("cards in hand:", gui.get_removed_cards())
            if current_deck:
                next_card = gui.replace_chosen_card(gui.get_card_pressed(), gui.get_removed_cards())
                gui.set_removed_cards(next_card)
                gui.draw_new_card(gui.get_card_pressed())
                print("updated order: cards in hand:", gui.get_removed_cards())
                add_to_waiting_list("DON", card_value, False, gui.get_player_num(), True)
            else:
                if len(gui.get_removed_cards()) == 3:
                    gui.draw_two_cards()
                    gui.draw_player_number(gui.get_player_num())
                    game_state = "TWO"
                    add_to_waiting_list("DON", card_value, False, gui.get_player_num(), True)
                elif len(gui.get_removed_cards()) == 2:
                    gui.draw_last_cards()
                    gui.draw_player_number(gui.get_player_num())
                    add_to_waiting_list("DON", card_value, False, gui.get_player_num(), True)
                    game_state = "ONE"
                else:
                    gui.create_screen()
                    gui.draw_player_number(gui.get_player_num())
                    gui.move_to_middle(gui.get_removed_cards(), gui.get_card_pressed())
                    print("Player Won")
                    logging.info('Player Won')
                    add_to_waiting_list("DON", card_value, True, gui.get_player_num(), True)
                    print("End Game")
            your_turn = False
            gui.set_discard_pile(discard_pile)
        else:
            gui.display_message("Card Chosen INVALID")
            gui.create_screen()
            gui.print_cards(game_state)
            # card_pressed = gui.choose_card()
        print("game state: " + str(game_state))
        logging.info("game state: " + str(game_state))
    except Exception as e:
        logging.error(f"Error pressing card: {e}")


def stop_connection():
    """
    Stops the connection to the server
    """
    global runs
    runs = False


def open_gui(cards_in_hand, deck, player_number):
    """
    Opens and initializes the GUI
    :param cards_in_hand: List of cards in hand
    :param deck: List of cards in the deck
    :param player_number: Player's number
    """
    global gui
    global discard_pile
    gui = GUI.GUI(deck, player_number, cards_in_hand, discard_pile, "")
    if gui is None:
        print("GUI IS NONE")
        logging.info("GUI IS NONE")
    gui.create_screen()
    if gui is None:
        print("GUI IS NONE")
        logging.info("GUI IS NONE")
    else:
        print("GUI IS NOT NONE")
        logging.info("GUI IS NOT NONE")


if __name__ == "__main__":
    logging.basicConfig(filename="client.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',)
    # Test the lowest_card function
    assert lowest_card([1, 2, 3, 4, 5, 6, 7, 8, 9]) == 1, "Test failed: Expected lowest yellow card to be 1"
    assert lowest_card([]) == 15, "Test failed: Expected empty list to return 15"
    assert lowest_card([10, 11, 12]) == 15, "Test failed: Expected no yellow cards to return 15"
    main()
