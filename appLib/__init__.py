#!/usr/bin/env python3

import sys
import time
import itertools
from appLib.mycurses import Screen, curses
import threading
import random
import math

per_h = 5
per_w = 15

x_max = 30
deter_line = x_max - 2*per_h
reserver_w = 3

keys = 'dfjk'
key_map = {key:num for (key, num) in zip(keys, itertools.count())}
nkeys = len(keys)

half = int(per_w/2)
pattern = ' '*half + '{0:s}' + ' '*(per_w-half-1)
pointers = tuple(pattern.format(key) for key in keys)


class App:
    def __init__(self, move=0):
        self.sep_time = 0.0 # will be reset, this value is meaningless after first loop.
        self.delay = 1
        self.clock = 0
        self.move = move
        self.hp_max = nkeys*per_w
        self.blocks = tuple(list() for _ in range(nkeys))
        # attention: ([])*nkeys creates only one list.
        time_next = time.time() + self.sep_time
        with Screen(x_max+reserver_w , nkeys*per_w) as self.screen:
            self.pointers = tuple(self.screen.addText(x_max, i*per_w,
                    words=pointers[i]) for i in range(nkeys))
            self.plugs = list(itertools.repeat(0, nkeys))
            self.notice = self.screen.addText(x_max+1, 0, words='Press <q> to to quit anytime.')
            self.hpbar = self.screen.addBlock(height=1, width=self.hp_max, x=x_max+2, y=0)
            while True:
                self.clock_func()
                time_next += self.sep_time
                time.sleep(max(time_next - time.time(), 0))


    def notice_update(self):
        self.notice.words = 'DISTANCE:{1:4d} HP:{0:2d}'.format(self.hpbar.width, self.move)

    def hp_change(self, num):
        self.hpbar.width = min(self.hp_max, self.hpbar.width+num)
        self.notice_update()
        if self.hpbar.width <= 0:
            self.gameover()

    def clock_func(self):
        self.clock += 1
        for key in self.screen.keys():
            if key == 'q':
                sys.exit()
            elif key in key_map:
                self.click(key_map[key])
        for i in range(nkeys):
            if self.clock == self.plugs[i]:
                self.pointers[i].attr = curses.A_NORMAL
        self.move_func()

    def click(self, i):
        if self.pointers[i].attr == curses.A_STANDOUT:
            return
        self.plugs[i] = self.clock + self.delay
        self.pointers[i].attr = curses.A_STANDOUT
        if self.blocks[i]:
            del self.blocks[i][0]
            self.hp_change(1)
        else:
            self.hp_change(-3)

    def move_func(self):
        self.move += 1
        self.notice_update()
        for col in self.blocks:
            for block in col:
                block.x += 1
        if not self.move%per_h:
            self.sep_time = 1/(30 - 18*math.exp(-self.move/2048))
            for i in range(nkeys):
                if random.uniform(0.0, 1.0) < 0.2 - 0.15*math.exp(-self.move/2048):
                    self.addBlock(i)
                if self.blocks[i] and self.blocks[i][0].x > deter_line:
                    del self.blocks[i][0]
                    self.hp_change(-per_w)
 
    def addBlock(self, pos):
        self.blocks[pos].append(self.screen.addBlock(height=per_h,
            width=per_w, x=-per_h, y=pos*per_w, x_max=x_max))

    def gameover(self):
        self.notice.words = 'Game Over! Total Distance:{0:4d}. Press <q> to quit.'.format(self.move)
        while True:
            if 'q' in self.screen.keys():
                sys.exit()
            time.sleep(self.sep_time)

if __name__ == '__main__':
    move = 0 if len(sys.argv) == 1 else int(sys.argv[1])
    App(move=move)


