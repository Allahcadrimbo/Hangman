# Grant Mitchell
# Networking Project
# The Game of Hangman
# Last Edited 12/11/18

import socket
import os
import sys
import time

# Define clear function which will clear the terminal
clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
# Define pause function which will pause the program until the user resumes it
pause = lambda: os.system("pause")
# Defining variables that will be needed later
port = 65535
ip = ""
socke = None
connection = None

# This is the main method of the program. It asks the user what it would like to do
def mainMenu():
    while 1:
        clear()
        print("~~~~~ Welcome To Hangman ~~~~~")
        print("1. Start a new game")
        print("2. Join an existing game")
        print("3. Exit Hangman")

        option = input('Choose what you would like to do: ')
        decision(option)


# The decision function takes the input from the mainMenu and executes the appropriate function for the chosen option
def decision(option):
    if option == '1':
        print(start_game())
    elif option == '2':
        print(join_game())
    elif option == '3':
        print(exit_game())
    else:
        print("Invalid Option. Try again!")
        time.sleep(3)
        return


# This function closes the program
def exit_game():
    sys.exit()


# The start_game function creates the server socket and listens for a connection with a client
def start_game():
    global socke, connection

    # Creating a TCP socket called socke
    socke = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Associates the socket with a specific IP and port
        socke.bind((ip, port))
        # Make it so the socket can accept connections which makes it a listening socket
        socke.listen(1)

        clear()
        print("Waiting for opponent to connect...")

        # Accept the connection
        connection, addr = socke.accept()

        clear()
        print("Connection to opponent established")
        pause()

    # Catch the exception if the server is unable to connect
    except Exception as e:
        clear()
        print("type error: " + str(e))
        print("Unable to establish connection to opponent")
        pause()
        return

    try:
        # Begin the game for the host
        begin_host_game()
        # After the game is complete the connection between the server and the client must be closed
        connection.close()

    # Catch the exception if there is an error connecting
    except Exception as e:
        clear()
        print("type error: " + str(e))
        print("Error connecting")
        pause()

    return


# This function creates the game and the game logic for the host (server)
def begin_host_game():
    # Defining variables needed
    global isDoubleLetter2, isDoubleLetter1
    isDoubleLetter1 = False
    isDoubleLetter2 = False
    clear()
    goal_word = input("Enter the word to be guessed: ")  # Word to be guessed by the player
    goal_word_letters = list(goal_word)  # List of letters in the goal_word
    known_letters = []  # The letters  in the goal word known
    incorrect_guesses = []  # the letters that were incorrect guesses
    guesses = 6  # The number of guesses the player gets

    # Iterates through the letters of the goal word
    for i in range(len(goal_word_letters)):
        # Adds the "" for each letter in the known_letters list
        known_letters.append(" ")
        # Checks if the first position and the second to last position is a double letter in the world
        if goal_word_letters[0] == goal_word_letters[i] and i != 0:
            isDoubleLetter1 = True
        if goal_word_letters[len(goal_word_letters) - 2] == goal_word_letters[i] and i != len(goal_word_letters) - 2:
            isDoubleLetter2 = True

    # If the first or second to last position is a double letter then the position for the known letter is changed if
    # not the position stays at the original index
    if not isDoubleLetter1:
        known_letters[0] = goal_word_letters[0]
    else:
        known_letters[1] = goal_word_letters[1]
    if not isDoubleLetter2:
        known_letters[len(goal_word_letters) - 2] = goal_word_letters[len(goal_word_letters) - 2]
    else:
        known_letters[len(goal_word_letters) - 1] = goal_word_letters[len(goal_word_letters) - 1]

    # Send the goal_word to the client
    connection.send(str.encode(goal_word))

    while 1:
        clear()

        # Creating the on screen display for the server (host)
        print("~~~~~~~~~    Hangman Host   ~~~~~~~~~")
        print("Goal Word: " + goal_word)
        print("Known Letters: " + str(known_letters))
        print("Incorrect Guesses: " + str(incorrect_guesses))
        print("Guesses Remaining = " + str(guesses))
        pick_drawing(guesses)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # Receive the move result from the client
        move_result = bytes.decode(connection.recv(1024))

        # If the client guesses the entire goal word then the game is over and the client won
        if move_result == "GuessedEntireWord":
            clear()
            print("You lost the game. Your opponent guessed the word!")
            pause()
            return
        # If the client guessed right the guess is added to the known_letters at the correct index
        elif move_result == "GuessedRight":
            # Receiving the letter and position of the guess from the client
            correct_letter = bytes.decode(connection.recv(1024))
            correct_letter_position = int(bytes.decode(connection.recv(1024)))
            known_letters[correct_letter_position] = correct_letter
        # If the client guessed wrong take the incorrect guess and append it onto the incorrect_guesses list
        # and subtract one from their guesses
        elif move_result == "GuessedWrong":
            incorrect_letter = bytes.decode(connection.recv(1024))
            incorrect_guesses.append(incorrect_letter)
            guesses -= 1

        # If the client ran out of guesses they lose the game and the game is ended
        elif move_result == "RanOutOfGuesses":
            print("Your opponent ran out of guesses. They could not guess the word " + goal_word + ". You won!")
            pause()
            return
        # If the client guessed all of the letters in the goal words then the client wins and the game ends.
        elif move_result == "GuessedGoalWord":
            print("Your opponent won. They guessed the word '" + goal_word + "'. You lost!")
            pause()
            return


# Creates the socket for the clients and connects to the servers listening socket
def join_game():
    global socke
    clear()
    # Creates the TCP socket called socke
    socke = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Prompts for the IP of the server to connect to
        ip = input('Enter the IP of the Game: ')
        # Associates the socket to that IP and the port
        socke.connect((ip, port))
        clear()
        print("You have connected to the game")
        pause()
    # Catches the exception if it fails to connect to the server
    except Exception as e:
        clear()
        print("type error: " + str(e))
        print("Failed to connect to the game")
        pause()
        return

    try:
        # Start the game for the client
        begin_player_game()
        # Close the socket after the game is complete
        socke.close()
    # Catches the exception if there is a connection error
    except Exception as e:
        clear()
        print("type error: " + str(e))
        print("Connection Error")
        pause()

    return


# Begins the game for the client
def begin_player_game():
    # Defines variables needed throughout
    global isDoubleLetter1
    global isDoubleLetter2
    isDoubleLetter1 = False
    isDoubleLetter2 = False
    clear()
    goal_word = bytes.decode(socke.recv(1024))  # receives the goal word from the server
    goal_word_letters = list(goal_word)  # The letters of the goal word
    known_letters = []  # The known letters in the goal word
    incorrect_guesses = []  # The letters that have been incorrectly guessed
    guesses = 6  # The number of guesses the client has

    # Iterates through the letters of the goal word
    for i in range(len(goal_word_letters)):
        # Adds the "" for each letter in the known_letters list
        known_letters.append(" ")
        # Checks if the first position and the second to last position is a double letter in the world
        if goal_word_letters[0] == goal_word_letters[i] and i != 0:
            isDoubleLetter1 = True
        if goal_word_letters[len(goal_word_letters) - 2] == goal_word_letters[i] and i != len(goal_word_letters) - 2:
            isDoubleLetter2 = True

    # If the first or second to last position is a double letter then the position for the known letter is changed if
    # not the position stays at the original index
    if not isDoubleLetter1:
        known_letters[0] = goal_word_letters[0]
    else:
        known_letters[1] = goal_word_letters[1]
    if not isDoubleLetter2:
        known_letters[len(goal_word_letters) - 2] = goal_word_letters[len(goal_word_letters) - 2]
    else:
        known_letters[len(goal_word_letters) - 1] = goal_word_letters[len(goal_word_letters) - 1]

    while 1:
        clear()
        # Declaring variables needed later
        global letterInGoal
        letterInGoal = False
        global letterInKnown
        letterInKnown = False
        global letterInIncorrect
        letterInIncorrect = False

        # Creating the on screen display for the client (player)
        print("~~~~~~~~~    Hangman Player   ~~~~~~~~~")
        print("Known Letters: " + str(known_letters))
        print("Incorrect Guesses: " + str(incorrect_guesses))
        print("Guesses Remaining = " + str(guesses))
        pick_drawing(guesses)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # Get the players guess
        entered_guess = input("Enter a letter or a word to guess: ")

        # If the player guessed the entire word they win the game and the game ends
        if entered_guess == goal_word:
            clear()
            print("Congratulations you won! You correctly guessed the word '" + goal_word + "'.")
            socke.send(str.encode("GuessedEntireWord"))
            pause()
            return

        # Check if the guessed letter is already in known_letters
        for i in range(len(goal_word_letters)):
            if entered_guess == known_letters[i]:
                letterInKnown = True
        # Check if the guessed letter us already in inCorrectGuesses
        for i in range(len(incorrect_guesses)):
            if entered_guess == incorrect_guesses[i]:
                letterInIncorrect = True

        # If the guess has already been guessed or is known then the player is asked to try again. There is no penalty.
        if letterInKnown | letterInIncorrect:
            print("That letter has already been guessed! Try again.")
            letterInKnown = False
            letterInIncorrect = False
            time.sleep(1)
        else:
            # Iterate through goal_word_letters and if entered guess is in the goal word then the guess is added to
            # the known letters list and the Guessed Right move is sent to the server
            for i in range(len(goal_word_letters)):
                if entered_guess == goal_word_letters[i]:
                    known_letters[i] = entered_guess
                    socke.send(str.encode("GuessedRight"))
                    time.sleep(.03)
                    # Send the guessed letter to the server
                    socke.send(str.encode(entered_guess))
                    time.sleep(.03)
                    # send the position of the letter to the server
                    socke.send(str.encode(str(i)))
                    time.sleep(.03)
                    print("Nice guess. That guess is correct!")
                    letterInGoal = True
                    time.sleep(1)
            # If the guess is incorrect
            if not letterInGoal:
                # Send the guess wrong move to the server
                socke.send(str.encode("GuessedWrong"))
                # send the letter to the server
                socke.send(str.encode(entered_guess))
                # Append the guess to the incorrect guesses to the list
                incorrect_guesses.append(entered_guess)
                # Decrement the guesses
                guesses -= 1
                print("Nice try. That guess is incorrect")
                time.sleep(1)
        # If the player guessed all of the letters in the goal word then the player wins
        if goal_word_letters == known_letters:
            clear()
            # Sends the GuessedGoalWord move to the server
            socke.send(str.encode("GuessedGoalWord"))
            print("Congratulations you correctly guessed the word " + goal_word + "!")
            pause()
            return
        # If the player runs out of guesses then the player loses the game
        if guesses < 1:
            # Send the RanOutOfGuesses move to the server
            socke.send(str.encode("RanOutOfGuesses"))
            clear()
            print("You ran out of guesses. Better luck next time! The word was " + goal_word)
            pause()
            return


# This function determines the state of the hangman drawing
def pick_drawing(guesses_remaining):
    if guesses_remaining == 6:
        guess_zero()
    elif guesses_remaining == 5:
        guess_one()
    elif guesses_remaining == 4:
        guess_two()
    elif guesses_remaining == 3:
        guess_three()
    elif guesses_remaining == 2:
        guess_four()
    elif guesses_remaining == 1:
        guess_five()
    elif guesses_remaining == 0:
        guess_six()


# The following functions are the possible hangman drawing states
def guess_six():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |       /|\ \n" +
          "      |       / \ \n" +
          "______|______     \n")


def guess_five():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |       /|\ \n" +
          "      |       /   \n" +
          "______|______     \n")


def guess_four():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |       /|\ \n" +
          "      |           \n" +
          "______|_____     \n")


def guess_three():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |       /|  \n" +
          "      |           \n" +
          "______|______     \n")


def guess_two():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |        |  \n" +
          "      |           \n" +
          "______|______     \n")


def guess_one():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |        0  \n" +
          "      |           \n" +
          "      |           \n" +
          "______|______     \n")


def guess_zero():
    print("      |---------- \n" +
          "      |        |  \n" +
          "      |           \n" +
          "      |           \n" +
          "      |           \n" +
          "______|______     \n")


if __name__ == "__main__":
    mainMenu()
