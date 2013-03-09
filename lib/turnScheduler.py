#!/usr/bin/env python
# -*- coding: utf-8-*-

'''
##########################################################
#
# Simple roguelike turn scheduler.
# Source: http://roguebasin.roguelikedevelopment.org/index.php/A_simple_turn_scheduling_system_--_Python_implementation
#
##########################################################
'''

# TODO: Some game actions might take more (reading a spellbook) or less (reloading a shotgun) time than a full turn. That is also easily handled by calculating a pseudo speed for those operations before calling schedule_turn. One problem is when a long turn is interrupted (e.g., "you stop digging" in NetHack). In that case the currently scheduled action would have to be canceled and a new action scheduled. Canceling the scheduled action is a small problem. One approach would be to store the ticks of the next action in the monster, so that the monster can ask the ticker to cancel the now unneeded action.


import random  # only needed for the fake monster

class Ticker(object):
    """Simple timer for roguelike games."""

    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def next_turn(self):
        things_to_do = self.schedule.pop(self.ticks, [])
        for obj in things_to_do:
            obj.do_turn()

###################################################################
#    Example main program

if __name__== "__main__":
    class Monster(object):
        """Fake monster for demo."""
        def __init__(self, ticker):
            self.ticker = ticker
            self.speed = 6 + random.randrange(1, 6)  # random speed in 7 - 12
            self.ticker.schedule_turn(self.speed, self) # schedule monsters 1st move

        def do_turn(self):
            print self, "gets a turn at", self.ticker.ticks # just print a message
            self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn

    ticker = Ticker()  #  create our ticker
    print ticker.schedule

    monsters = []  #  create some monsters for the demo
    while len(monsters) < 5:
        monsters.append(Monster(ticker))
    print ticker.schedule

    while ticker.ticks < 51:  #  our main program loop
        if ticker.ticks in [10, 20, 30, 40, 50]:
            print ticker.schedule
        ticker.ticks += 1
        ticker.next_turn()