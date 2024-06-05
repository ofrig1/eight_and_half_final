import socket
import logging
import GUI
import pygame
import Game

#  constants
MAX_PACKET = 1024
IP = '127.0.0.1'
PORT = 8820
SEPERATOR = '$'


def receive_deck(my_socket):
    # Receive the string message from the server
    message_str = my_socket.recv(4096).decode()  # Adjust buffer size as needed

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


def hand_out_cards(deck):
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
    message = f"{msg_type}${current_card}${did_win}${player}${did_turn}"
    my_socket.send(message.encode())


def lowest_card(cards_in_hand):
    lowest_card_value = 15
    for card in cards_in_hand:
        if (1 <= card <= 4 or 6 <= card <= 9) and card < lowest_card_value:
            lowest_card_value = card
    return lowest_card_value  # if equal to 15 means no yellow cards


def receive_update(my_socket):
    message_str = my_socket.recv(4096).decode()  # Adjust buffer size as needed

    # Check if the message is empty
    if not message_str:
        raise ValueError("Received empty message from server")

    # Check if the message starts with '$'
    if not message_str.startswith('UPD$'):
        raise ValueError("Invalid message format: Message does not start with 'DON$'")

    # Remove the leading '$' character
    message_str = message_str[4:]

    # Convert the string back into a list of integers
    new_card_placed, did_win, player = message_str.split(SEPERATOR)

    return new_card_placed, did_win, int(player)


def receive_msg(my_socket):
    message_str = my_socket.recv(4096).decode()  # Adjust buffer size as needed

    # Check if the message is empty
    if not message_str:
        raise ValueError("Received empty message from server")

    if message_str.startswith('UPD$'):
        message_str = message_str[4:]
        return "UPD", message_str
    elif message_str.startswith('PLA$'):
        message_str = message_str[4:]
        return "PLA", message_str
    # Check if the message starts with '$'
    else:
        raise ValueError("Invalid message format: Message does not start with 'DON$' or 'PLA$")


def main():
    """
    Sends messages to server and get responses
    :return:
    """
    discard_pile = []
    logging.basicConfig(filename="client.log", level=logging.DEBUG)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((IP, PORT))
        is_connect = my_socket.recv(1024).decode()
        if is_connect != "Connected":
            print(is_connect)
            my_socket.close()
            return
        # print("Joined Game")
        player_number = my_socket.recv(1024).decode()
        print("Player Number: " + player_number)
        # welcome_page = welcome.WelcomePage(player_number)
        deck = receive_deck(my_socket)
        print(deck)
        cards_in_hand, deck = hand_out_cards(deck)
        print("Cards in hand:", cards_in_hand)
        print("Remaining deck:", deck)
        send_message(my_socket, 'LOW', lowest_card(cards_in_hand), False, player_number, True)
        gui = GUI.GUI(deck, player_number, cards_in_hand, discard_pile, "")
        gui.create_screen()
        gui.print_card()
        game = GAME.GAME(discard_pile, 0, cards_in_hand)
        new_card_placed, did_win, player = receive_update(my_socket)
        if new_card_placed == "EMPTY":
            gui.redo()
        else:
            gui.move_to_middle(discard_pile, new_card_placed)
        if player == player_number:
            print("Are cards valid?", game.have_valid_card())
            if not game.have_valid_card():
                gui.display_message("No Valid Card")
                if discard_pile:
                    last_card = discard_pile[-1]
                else:
                    last_card = []
                send_message(my_socket, "DON", last_card, False, player_number, False)
            else:
                card_pressed = gui.choose_card()
                card_value = cards_in_hand[card_pressed - 1]
                game = GAME.GAME(discard_pile, card_value, cards_in_hand)
                print("Is card valid?", game.is_card_valid())
                while not game.is_card_valid():
                    gui.display_message("Card Chosen INVALID")
                    gui.create_screen()
                    gui.print_cards("")
                    card_pressed = gui.choose_card()
                    card_value = cards_in_hand[card_pressed - 1]
                    game = GAME.GAME(discard_pile, card_value, cards_in_hand)
                gui.move_to_middle(cards_in_hand, card_pressed)
                next_card = gui.replace_chosen_card(card_pressed, cards_in_hand)
                if next_card is not False:
                    gui.draw_new_card(card_pressed)
                    send_message(my_socket, "DON", card_value, False, player_number, True)

                else:
                    if len(cards_in_hand) == 2:
                        gui.draw_two_cards()
                        send_message(my_socket, "DON", card_value, False, player_number, True)
                    elif len(cards_in_hand) == 1:
                        gui.draw_last_cards()
                        send_message(my_socket, "DON", card_value, False, player_number, True)
                    else:
                        print("Player Won")
                        send_message(my_socket, "DON", card_value, True, player_number, True)
                print("End Game")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    except socket.error as err:
        print('received socket error ' + str(err))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        logging.debug("Closing Client Socket")
        # try:
        # if my_socket is not None and is_socket_connected(my_socket):
        # my_socket.send(protocol_client_send('EXIT').encode())
        # finally:
        my_socket.close()


if __name__ == "__main__":
    main()
