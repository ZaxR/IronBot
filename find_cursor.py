import time

import pyautogui


if __name__ == '__main__':
    print('Press Ctrl-C to quit.')
    try:
        while True:
            # Get and print the mouse coordinates.
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print("\r", positionStr, end="", flush=True)
            time.sleep(0.25)
    except KeyboardInterrupt:
        print('\nDone.')
