import curses
import time
import itertools
import operator


BACK_GROUD = (ord(' '), curses.A_NORMAL)
SOLID = (ord(' '), curses.A_STANDOUT)

class Widget:
    def __init__(self, screen, xycas):
        self.__dict__['screen'] = screen
        self.__dict__['xycas'] = set()
        self.__dict__['xys'] = set()
        Widget.__setattr__(self, 'xycas', xycas)

    def __setattr__(self, name, value):
        if name == 'xycas':
            xycas_old = self.xycas
            xys_old = self.xys
            self.__dict__['xycas'] = set(value)
            self.__dict__['xys'] = set((x, y) for (x, y, c, a) in self.xycas)
            for (x, y) in (xys_old - self.xys):
                self.screen.win.addch(x, y, *BACK_GROUD)
            for (x, y, c, a) in (self.xycas - xycas_old):
                self.screen.win.addch(x, y, c, a)
            self.screen.win.move(self.screen.height, self.screen.width-1)
        else:
            raise ValueError('Only attribute xycas can be modified.') 

    def __del__(self):
        Widget.__setattr__(self, 'xycas', set())


class Block(Widget):
    def __init__(self, screen, height, width, x, y,
            *, x_min=0, y_min=0, x_max=-1, y_max=-1):
        self.__dict__['x'] = x
        self.__dict__['y'] = y
        self.__dict__['height'] = height
        self.__dict__['width'] = width
        self.__dict__['x_max'] = x_max if x_max != -1 else screen.height
        self.__dict__['x_min'] = x_min
        self.__dict__['y_max'] = y_max if y_max != -1 else screen.width
        self.__dict__['y_min'] = y_min
        Widget.__init__(self, screen, self.get_xycas())

    def get_xycas(self):
        xs = range(max(self.x, self.x_min), min(self.x+self.height, self.x_max))
        ys = range(max(self.y, self.y_min), min(self.y+self.width, self.y_max))
        return map(operator.add, itertools.product(xs, ys), itertools.repeat(SOLID))

    def __setattr__(self, name, value):
        if name in ('x', 'y', 'height', 'width',
                'x_min', 'x_max', 'y_min', 'y_max'):
            self.__dict__[name] = value
            Widget.__setattr__(self,'xycas', self.get_xycas())
        else:
            Widget.__setattr__(self, name, value)

class Text(Widget):
    def __init__(self, screen, x, y, words='', attr=curses.A_NORMAL, limit=-1):
        self.__dict__['x'] = x
        self.__dict__['y'] = y
        self.__dict__['attr'] = attr
        self.__dict__['limit'] =  limit if limit != -1 else (screen.width-y)
        self.__dict__['words'] = words
        Widget.__init__(self, screen, self.get_xycas())

    def get_xycas(self):
        ycs = zip(range(self.y, self.y+self.limit), self.words)
        return ((self.x, y, c, self.attr) for (y, c) in ycs)

    def __setattr__(self, name, value):
        if name in ('words', 'x', 'y', 'limit', 'attr'):
            self.__dict__[name] = value
            Widget.__setattr__(self, 'xycas', self.get_xycas())
        else:
            Widget.__setattr__(self, name, value)

class Screen:
    def __init__(self, height, width):
        self.height = height
        self.width = width
 
    def __enter__(self):
        self.stdscr = curses.initscr()
        self.win = curses.newwin(self.height+1, self.width)
        self.win.nodelay(True)
        # +1 is intended to prevent overflow
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.noecho()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        # print(exc_type, exc_value, exc_traceback)

    def keys(self):
        res = ''
        while True:
            try:
                res += self.win.getkey()
            except Exception:
                break
        return res

    def refresh(self):
        self.win.refresh() # Most of time, a refresh is not neccessary.

    def addBlock(self, *args, **kwargs):
        return Block(self, *args, **kwargs)

    def addText(self, *args, **kwargs):
        return Text(self, *args, **kwargs)

