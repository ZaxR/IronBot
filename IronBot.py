import math
from random import randint, uniform
import sys
import time

import cv2
import numpy as np
import pyautogui as pag


class MineBot(object):
    """
    Iron mining bot for the Dwarven Mines, using 3/3 rocks. Currently  
    Bot generates:
        One full run in ~155 seconds, for ~23.25 runs/hour
        ~22.8k xp/hr,
        ~650 iron ore/hr,
        ~190.5k gp/hr (assuming a 293gp/ore price)
    """
    def __init__(self):
        pass

    def mine_loop(self, rock_locations, triggers, mininglap):
        order = ['rock1', 'rock2', 'rock3']
        trigger_order = ['rock1iron', 'rock1noiron', 'rock2iron', 'rock2noiron', 'rock3iron', 'rock3noiron']

        for i in range(len(order)):
            # Checks for full inventory.
            if not self.image_match((2352, 682, 63, 55), 'triggers/bankslot.png'):
                return True

            # Checks for scorpions and moves to the location of rock #3.
            if i == 2:
                self.random_coordinate(rock_locations['movetorock3'])
                self.check_for_scorpion((rock_locations['movetorock3'][0], rock_locations['movetorock3'][1],
                                         rock_locations['movetorock3'][2] + 250, rock_locations['movetorock3'][3] + 250))
                pag.click()

            self.random_coordinate(rock_locations[order[i]])
            self.wait_for_trigger(triggers[trigger_order[(i*2)]])  # wait for iron
            pag.click()
            self.wait_for_trigger(triggers[trigger_order[(i*2)+1]])  # wait for success
            self.random_wait(0.05, 0.1)

        # Resets location for the beginning of the next loop.
        self.random_coordinate(rock_locations['reset'])
        self.check_for_scorpion((rock_locations['reset'][0], rock_locations['reset'][1],
                                 rock_locations['reset'][2] + 250, rock_locations['reset'][3] + 250))
        pag.click()
        self.wait_for_trigger((1700, 50, 150, 150, 'triggers/reset_check.png'))  # check to make sure made it to right location

        return

    def bank_loop(self, bank_locations, triggers):
        """Makes a trip to the bank to deposit the iron ore. Takes 16-17 seconds"""
        order = ['dgdoordown', 'depositbox', 'depositbutton', 'dgdoorup', 'startlocation']
        waits = [(0.1, 0.2), (0.1, 0.2), (0.1, 0.2), (5, 6), (0.1, 0.2)]

        for i in range(len(order)):
            self.random_coordinate(bank_locations[order[i]])
            if i in range(4):
                self.wait_for_trigger(triggers[order[i]])
            if i == 4:
                self.check_for_scorpion((947, 1195, 250, 250))
            pag.click()
            self.random_wait(waits[i][0], waits[i][1])

    def drop_loop(self, keybind='0'):
        r = randint(28, 32)
        t = uniform(4.8, 7)
        clicktime = t/r
        for _ in range(r):
            pag.keyDown(keybind)
            self.random_wait(clicktime - .04, clicktime + .04)

    def bank_or_drop(self):
        while True:
            answer = input('Would you like to 1) bank (takes an extra ~10 seconds/inventory) or 2) drop the ore? ')
            if answer.lower() in ['b', 'ban', 'bnk', 'bakn', 'bnak', 'bank', 's', 'save', 'y', 'yes']:
                print('Banking selected.')
                return 'bank'
            elif answer.lower() in ['d', 'dro', 'drp', 'drpo', 'dorp', 'drop', 'n', 'no']:
                print('Dropping selected.')
                return 'drop'
            else:
                print('Not a valid option.  Please try again.')

    def random_coordinate(self, location):
        """Moves cursor to random locaction still above the object to be clicked"""
        x = randint(location[0], location[0]+location[2])
        y = randint(location[1], location[1]+location[3])
        time = self.travel_time(x, y)

        return pag.moveTo(x, y, time)

    def travel_time(self, x2, y2):
        """Calculates cursor travel time in seconds per 240-270 pixels, based on a variable rate of movement"""
        rate = uniform(0.09, 0.15)
        x1, y1 = pag.position()
        distance = math.sqrt(math.pow(x2-x1, 2)+math.pow(y2-y1, 2))

        return max(uniform(.08, .12), rate * (distance/randint(250, 270)))

    def image_match(self, r, img):
        pag.screenshot('triggers/screenie.png', region=r)
        screen = cv2.imread('triggers/screenie.png')
        template = cv2.imread(img)

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        threshold = .80
        loc = np.where(res >= threshold)
        if len(loc[0]) > 0:
            return True

        return False

    def wait_for_trigger(self, triggers):
        """Checks to see if the proper message is on screen to indicate that the rock is ready to mine"""
        r = triggers[0], triggers[1], triggers[2], triggers[3]
        img = triggers[4]
        while self.image_match(r, img) == False:
            self.random_wait(0.1, 0.2)

        return self.image_match(r, img)

    def random_wait(self, min=0.25, max=0.50):
        """Waits a random number of seconds between two numbers (0.25 and 0.50 default) to mimic human reaction time"""
        return time.sleep(uniform(min, max))

    def check_for_scorpion(self, r):
        if self.image_match(r, 'triggers/attack.png'):
            pag.click(button='right')
            print("Successfully avoided a scorpion.")
            pag.moveRel(randint(-75, 75), randint(58, 78))

    def logout(self, logout_location=(1194, 955, 167, 14)):
        pag.keyDown('escape')
        self.random_wait()
        pag.click(self.random_coordinate(logout_location))
        sys.exit('Successful exit')

    def pause(self):
        pass

if __name__ == '__main__':

    mb = MineBot()
    rock_locations = {'rock1': (1243, 569, 55, 62), 'rock2': (1138, 695, 34, 39),
                      'movetorock3': (962, 823, 50, 50), 'rock3': (1128, 691, 37, 56),
                      'reset': (1465, 570, 50, 50)}

    bank_locations = {'dgdoordown': (1630, 230, 70, 100), 'depositbox': (1079, 1086, 104, 71),
                      'depositbutton': (1333, 849, 30, 15), 'dgdoorup': (1625, 240, 45, 200),
                      'startlocation': (947, 1195, 71, 65)}

    rock_triggers = {'rock1iron': (1243, 569, 350, 200, 'triggers/mine_iron_ore_rocks.png'),
                     'rock1noiron': (1243, 569, 275, 200, 'triggers/mine_rocks.png'),
                     'rock2iron': (1144, 695, 350, 200, 'triggers/mine_iron_ore_rocks.png'),
                     'rock2noiron': (1144, 695, 275, 200, 'triggers/mine_rocks.png'),
                     'rock3iron': (1128, 691, 350, 200, 'triggers/mine_iron_ore_rocks.png'),
                     'rock3noiron': (1128, 691, 275, 200, 'triggers/mine_rocks.png')}

    bank_triggers = {'dgdoordown': (1630, 230, 470, 200, 'triggers/enter_mysterious_entrance.png'),
                     'depositbox': (1079, 1086, 500, 200, 'triggers/bank_deposit_box.png'),
                     'depositbutton': (1175, 750, 350, 100, 'triggers/deposit_button_hover.png'),
                     'dgdoorup': (1625, 240, 350, 300, 'triggers/exit_mysterious_door.png')}

    print('Your character must be in the NorthWest tile by the two iron ore rocks in the Dwarven Mines.\n'
          'Also, the up arrow must be pushed as high as possible, and rotation must be the same as on first login.\n'
          'Press Ctrl-F2 to exit.')

    answer = mb.bank_or_drop()

    time.sleep(5)

    try:
        lap = 0
        while True:
            start_time = time.time()
            mininglap = 1
            while True:
                full = mb.mine_loop(rock_locations, rock_triggers, mininglap)
                if full:
                    break
                mininglap += 1
            if answer == 'bank':
                mb.bank_loop(bank_locations, bank_triggers)
            else:
                mb.drop_loop()
            lap += 1
            laptime = time.time()-start_time
            print("Trip number {tripno} took {time} seconds, which is a {xp} xp/hour and "
                  "{ore} iron ore/hour pace.".format(tripno=lap, time=round(laptime, 2),
                                                    xp=('{0:,.0f}'.format(60 / (laptime / 60) * 28 * 35)),
                                                    ore=('{0:,.0f}'.format(60/(laptime/60)*28))))
    except KeyboardInterrupt:
        sys.exit()
