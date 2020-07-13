# Displays a string of characters on a line. On the next line, the characters are shown again
#   but shifted over one and the last character is now the first.
# The keyboard module provided much help in capturing the keys necessary.
# This code is not as fluid as the initial idea, but work will be done to make it so.
# NOTE!!!! The file will need to be run as an administrator as keyboard can log keystrokes.
#    _darwinkeyboard.py line 420 is the offender. Maybe you can figure a way around it...

from time import sleep
import keyboard
import logging

vel = 0
string = ["0123456789", ".............................!"]

# The logging was very helpful when figuring out how the keyboard module works
logging.basicConfig(level=logging.DEBUG)
logging.disable(logging.DEBUG)


def delta(char):
    global vel

    if char == 'u':
        logging.debug("Speeding up.")
        # Decreases the waiting period of the next loop, speeding it up.
        vel -= 1
        # Helps filter out the input of keyboard events.
        # #     Without it, one key press is recognized as several key presses
        keyboard.wait()

    if char == 'd':
        logging.debug("Slowing down.")
        # Increases the waiting period of the next loop, slowing it down.
        vel += 1
        keyboard.wait()


def check(text):
    length = len(text) - 1
    text2 = []  # The empty list where the function argument will be copied
    global vel
    vel = .03

    for i in range(length + 1):
        # Initially I coded this manually but then remembered that there is an api.
        #   Using the functions significantly decreased the line count.
        #   STUDY THE API!!!
        text2.append(text[i])

    while True:
        # Takes off the last entry and inserts it into index 0
        text2.insert(0, text2.pop())

        # pip install keyboard
        # https://github.com/boppreh/keyboard#keyboard.get_hotkey_name
        # If the up arrow is pressed, it will execute function delta with 'u' arg
        keyboard.add_hotkey("up", lambda: delta('u'))
        keyboard.add_hotkey("down", lambda: delta('d'))

        # printing a list normally will show '1', '2' etc. and I didn't want the extra characters on the screen
        #   This way, only the list elements are shown
        for item in text2:
            print(item, end = "")

        # Shows the speed / vel /sleep wait time
        print("---->", vel, end = "\n")

        if vel <= 0:
            vel = 0.01

        # Waits before showing the next line.
        sleep(vel)


check(string)
